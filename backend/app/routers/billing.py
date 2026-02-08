"""
Billing Router
- View bills
- Pay bills
- Payment history
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.bill import Bill, BillStatus, UtilityType
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.schemas.bill import (
    BillResponse, BillListResponse, BillPaymentRequest, 
    PaymentResponse, PaymentHistoryResponse
)
from app.middleware.auth import get_current_user
from app.utils.generators import generate_transaction_id, generate_receipt_number, generate_qr_code
from app.utils.audit import create_audit_log

router = APIRouter(prefix="/bills", tags=["Billing"])


@router.get("/", response_model=BillListResponse)
async def get_user_bills(
    utility_type: Optional[UtilityType] = None,
    status_filter: Optional[BillStatus] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all bills for current user"""
    query = select(Bill).where(Bill.user_id == user.id)
    
    if utility_type:
        query = query.where(Bill.utility_type == utility_type)
    if status_filter:
        query = query.where(Bill.status == status_filter)
    
    query = query.order_by(Bill.due_date.desc())
    
    result = await db.execute(query)
    bills = result.scalars().all()
    
    # Calculate total outstanding and utility summary
    total_outstanding = sum(b.outstanding_amount for b in bills)
    utility_summary = {}
    for bill in bills:
        ut = bill.utility_type.value
        if ut not in utility_summary:
            utility_summary[ut] = Decimal(0)
        utility_summary[ut] += bill.outstanding_amount
    
    # Convert to response
    bill_responses = []
    for bill in bills:
        is_overdue = bill.due_date < date.today() and bill.status in [BillStatus.PENDING, BillStatus.PARTIALLY_PAID]
        days_until_due = (bill.due_date - date.today()).days if bill.due_date >= date.today() else None
        
        bill_responses.append(BillResponse(
            id=bill.id,
            bill_number=bill.bill_number,
            account_number=bill.account_number,
            utility_type=bill.utility_type,
            billing_period_start=bill.billing_period_start,
            billing_period_end=bill.billing_period_end,
            units_consumed=bill.units_consumed,
            base_amount=bill.base_amount,
            taxes=bill.taxes,
            surcharges=bill.surcharges,
            late_fee=bill.late_fee,
            total_amount=bill.total_amount,
            amount_paid=bill.amount_paid,
            outstanding_amount=bill.outstanding_amount,
            bill_date=bill.bill_date,
            due_date=bill.due_date,
            status=bill.status,
            is_overdue=is_overdue,
            days_until_due=days_until_due
        ))
    
    return BillListResponse(
        bills=bill_responses,
        total_outstanding=total_outstanding,
        utility_summary={k: float(v) for k, v in utility_summary.items()}
    )


@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill_details(
    bill_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific bill details"""
    result = await db.execute(
        select(Bill).where(and_(Bill.id == bill_id, Bill.user_id == user.id))
    )
    bill = result.scalar_one_or_none()
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    await create_audit_log(
        db=db,
        action="BILL_VIEW",
        actor_type="user",
        user_id=user.id,
        resource_type="bill",
        resource_id=bill.id,
        ip_address=request.client.host if request.client else None,
    )
    
    is_overdue = bill.due_date < date.today() and bill.status in [BillStatus.PENDING, BillStatus.PARTIALLY_PAID]
    days_until_due = (bill.due_date - date.today()).days if bill.due_date >= date.today() else None
    
    return BillResponse(
        id=bill.id,
        bill_number=bill.bill_number,
        account_number=bill.account_number,
        utility_type=bill.utility_type,
        billing_period_start=bill.billing_period_start,
        billing_period_end=bill.billing_period_end,
        units_consumed=bill.units_consumed,
        base_amount=bill.base_amount,
        taxes=bill.taxes,
        surcharges=bill.surcharges,
        late_fee=bill.late_fee,
        total_amount=bill.total_amount,
        amount_paid=bill.amount_paid,
        outstanding_amount=bill.outstanding_amount,
        bill_date=bill.bill_date,
        due_date=bill.due_date,
        status=bill.status,
        is_overdue=is_overdue,
        days_until_due=days_until_due
    )


@router.post("/pay", response_model=PaymentResponse)
async def pay_bill(
    request: Request,
    payment_data: BillPaymentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate bill payment.
    In production, this would redirect to payment gateway.
    For demo, payment is simulated as successful.
    """
    # Get bill
    result = await db.execute(
        select(Bill).where(and_(Bill.id == payment_data.bill_id, Bill.user_id == user.id))
    )
    bill = result.scalar_one_or_none()
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    if bill.status == BillStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bill is already paid"
        )
    
    if payment_data.amount > bill.outstanding_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount exceeds outstanding balance"
        )
    
    # Generate transaction details
    transaction_id = generate_transaction_id()
    receipt_number = generate_receipt_number()
    
    # Get previous payment hash for chain
    last_payment = await db.execute(
        select(Payment.transaction_hash)
        .where(Payment.user_id == user.id)
        .order_by(Payment.id.desc())
        .limit(1)
    )
    previous_hash = last_payment.scalar_one_or_none()
    
    # Compute transaction hash
    import hashlib
    import json
    hash_data = json.dumps({
        "transaction_id": transaction_id,
        "bill_id": bill.id,
        "amount": str(payment_data.amount),
        "timestamp": datetime.utcnow().isoformat(),
        "previous_hash": previous_hash or "GENESIS"
    }, sort_keys=True)
    transaction_hash = hashlib.sha256(hash_data.encode()).hexdigest()
    
    # Create payment record
    payment = Payment(
        transaction_id=transaction_id,
        gateway_transaction_id=f"SIM_{transaction_id}",  # Simulated
        user_id=user.id,
        bill_id=bill.id,
        amount=payment_data.amount,
        convenience_fee=Decimal("0"),
        total_amount=payment_data.amount,
        payment_method=PaymentMethod(payment_data.payment_method),
        status=PaymentStatus.SUCCESS,  # Simulated success
        receipt_number=receipt_number,
        transaction_hash=transaction_hash,
        previous_hash=previous_hash,
        initiated_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    
    # Generate QR code for receipt
    qr_data = f"SUVIDHA|{receipt_number}|{transaction_id}|{payment_data.amount}"
    payment.receipt_qr_code = generate_qr_code(qr_data)
    
    db.add(payment)
    
    # Update bill
    bill.amount_paid += payment_data.amount
    bill.outstanding_amount -= payment_data.amount
    
    if bill.outstanding_amount <= 0:
        bill.status = BillStatus.PAID
    elif bill.amount_paid > 0:
        bill.status = BillStatus.PARTIALLY_PAID
    
    await create_audit_log(
        db=db,
        action="BILL_PAYMENT_SUCCESS",
        actor_type="user",
        user_id=user.id,
        resource_type="payment",
        resource_id=payment.id,
        description=f"Payment of Rs.{payment_data.amount} for bill {bill.bill_number}",
        ip_address=request.client.host if request.client else None,
        metadata={
            "transaction_id": transaction_id,
            "bill_number": bill.bill_number,
            "amount": str(payment_data.amount)
        }
    )
    
    await db.flush()
    
    return PaymentResponse(
        transaction_id=transaction_id,
        bill_id=bill.id,
        amount=payment_data.amount,
        status="SUCCESS",
        receipt_number=receipt_number,
        receipt_qr=payment.receipt_qr_code,
        payment_time=datetime.utcnow(),
        message="Payment successful. Receipt generated."
    )


@router.get("/history/all", response_model=List[PaymentHistoryResponse])
async def get_payment_history(
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment history for current user"""
    result = await db.execute(
        select(Payment, Bill)
        .join(Bill, Payment.bill_id == Bill.id)
        .where(Payment.user_id == user.id)
        .order_by(Payment.initiated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    payments = result.all()
    
    return [
        PaymentHistoryResponse(
            transaction_id=p.Payment.transaction_id,
            bill_number=p.Bill.bill_number,
            utility_type=p.Bill.utility_type,
            amount=p.Payment.total_amount,
            payment_method=p.Payment.payment_method,
            status=p.Payment.status.value,
            payment_time=p.Payment.completed_at or p.Payment.initiated_at,
            receipt_number=p.Payment.receipt_number
        )
        for p in payments
    ]
