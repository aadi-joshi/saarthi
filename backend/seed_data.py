"""
Database seed script for demo data
Run this to populate the database with sample data for hackathon demo
"""
import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

from app.database import init_db, async_session_maker
from app.models import (
    User, Admin, Bill, Payment, Grievance, ConnectionRequest, 
    Notification, Document, AuditLog
)
from app.models.admin import AdminRole
from app.models.bill import BillStatus, UtilityType
from app.models.grievance import GrievanceStatus, GrievanceCategory
from app.models.connection import ConnectionStatus, ConnectionType
from app.models.notification import NotificationType
from app.utils.encryption import encrypt_data, hash_data
from app.utils.security import hash_password
from app.utils.generators import generate_tracking_id, generate_application_number


async def seed_database():
    """Seed the database with demo data"""
    await init_db()
    
    async with async_session_maker() as db:
        print("🌱 Seeding database...")
        
        # Create Admin users
        print("  Creating admin users...")
        admin = Admin(
            username="admin",
            email="admin@suvidha.gov.in",
            password_hash=hash_password("admin123"),
            full_name="System Administrator",
            department="IT Department",
            role=AdminRole.SUPER_ADMIN,
            is_active=True,
        )
        db.add(admin)
        
        operator = Admin(
            username="operator",
            email="operator@suvidha.gov.in",
            password_hash=hash_password("operator123"),
            full_name="Kiosk Operator",
            department="Customer Service",
            role=AdminRole.OPERATOR,
            is_active=True,
        )
        db.add(operator)
        
        # Create Demo user
        print("  Creating demo user...")
        demo_mobile = "9876543210"
        demo_user = User(
            mobile_encrypted=encrypt_data(demo_mobile),
            mobile_hash=hash_data(demo_mobile),
            full_name="Rajesh Kumar",
            email_encrypted=encrypt_data("rajesh@example.com"),
            consumer_number="ELEC-2024-001234",
            address_encrypted=encrypt_data("123, MG Road, Sector 15, Noida, UP - 201301"),
            preferred_language="en",
            is_verified=True,
            is_active=True,
        )
        db.add(demo_user)
        await db.flush()
        
        # Create Bills for demo user
        print("  Creating sample bills...")
        bills_data = [
            {
                "utility_type": UtilityType.ELECTRICITY,
                "bill_number": "ELEC-2024-0001",
                "account_number": "ELEC-2024-001234",
                "total_amount": Decimal("2450.00"),
                "outstanding_amount": Decimal("2450.00"),
                "units_consumed": 245,
                "status": BillStatus.PENDING,
            },
            {
                "utility_type": UtilityType.GAS,
                "bill_number": "GAS-2024-0001",
                "account_number": "GAS-2024-005678",
                "total_amount": Decimal("890.00"),
                "outstanding_amount": Decimal("890.00"),
                "units_consumed": 12,
                "status": BillStatus.PENDING,
            },
            {
                "utility_type": UtilityType.WATER,
                "bill_number": "WTR-2024-0001",
                "account_number": "WTR-2024-009012",
                "total_amount": Decimal("450.00"),
                "outstanding_amount": Decimal("0.00"),
                "amount_paid": Decimal("450.00"),
                "units_consumed": 15000,
                "status": BillStatus.PAID,
            },
            {
                "utility_type": UtilityType.ELECTRICITY,
                "bill_number": "ELEC-2024-0002",
                "account_number": "ELEC-2024-001234",
                "total_amount": Decimal("1850.00"),
                "outstanding_amount": Decimal("1850.00"),
                "units_consumed": 185,
                "status": BillStatus.OVERDUE,
            },
        ]
        
        for i, bill_data in enumerate(bills_data):
            bill = Bill(
                user_id=demo_user.id,
                billing_period_start=date.today() - timedelta(days=60 + i*30),
                billing_period_end=date.today() - timedelta(days=30 + i*30),
                bill_date=date.today() - timedelta(days=25 + i*30),
                due_date=date.today() + timedelta(days=5 - i*15),
                base_amount=bill_data["total_amount"] * Decimal("0.85"),
                taxes=bill_data["total_amount"] * Decimal("0.10"),
                surcharges=bill_data["total_amount"] * Decimal("0.05"),
                **bill_data
            )
            db.add(bill)
        
        # Create Grievances
        print("  Creating sample grievances...")
        grievances_data = [
            {
                "category": GrievanceCategory.POWER_OUTAGE,
                "subject": "Frequent power cuts in Sector 15",
                "description": "Power cuts happening 3-4 times daily for past week",
                "status": GrievanceStatus.IN_PROGRESS,
            },
            {
                "category": GrievanceCategory.BILLING_DISPUTE,
                "subject": "Incorrect meter reading",
                "description": "Bill shows 450 units but actual reading is 245 units",
                "status": GrievanceStatus.ACKNOWLEDGED,
            },
            {
                "category": GrievanceCategory.WATER_SUPPLY,
                "subject": "Low water pressure",
                "description": "Water pressure very low since last month",
                "status": GrievanceStatus.RESOLVED,
            },
        ]
        
        for grv_data in grievances_data:
            grievance = Grievance(
                tracking_id=generate_tracking_id("GRV"),
                user_id=demo_user.id,
                location_address="Sector 15, Noida",
                location_pin="201301",
                assigned_department="Electricity Department",
                priority=2,
                expected_resolution_date=datetime.utcnow() + timedelta(hours=48),
                **grv_data
            )
            db.add(grievance)
        
        # Create Connection Request
        print("  Creating sample connection request...")
        connection = ConnectionRequest(
            application_number=generate_application_number("CON"),
            user_id=demo_user.id,
            connection_type=ConnectionType.GAS_DOMESTIC,
            applicant_name="Rajesh Kumar",
            applicant_mobile="9876543210",
            property_type="RESIDENTIAL",
            property_address="456, Sector 20, Noida",
            property_pin="201301",
            status=ConnectionStatus.SITE_INSPECTION_PENDING,
            current_step=3,
            total_steps=5,
            application_fee=Decimal("100"),
            connection_fee=Decimal("2000"),
            security_deposit=Decimal("500"),
            total_fee=Decimal("2600"),
            fee_paid=True,
        )
        db.add(connection)
        
        # Create Notifications
        print("  Creating sample notifications...")
        notifications_data = [
            {
                "title": "Scheduled Maintenance",
                "title_hi": "निर्धारित रखरखाव",
                "message": "Power supply will be interrupted on Sunday 9 AM - 1 PM for maintenance work in Sector 15-20.",
                "message_hi": "रखरखाव कार्य के लिए रविवार को सुबह 9 बजे से दोपहर 1 बजे तक सेक्टर 15-20 में बिजली आपूर्ति बाधित रहेगी।",
                "notification_type": NotificationType.MAINTENANCE,
                "is_banner": True,
            },
            {
                "title": "Pay Before Due Date",
                "title_hi": "नियत तारीख से पहले भुगतान करें",
                "message": "Avoid late fees! Pay your utility bills before the due date.",
                "message_hi": "विलंब शुल्क से बचें! नियत तारीख से पहले अपने उपयोगिता बिलों का भुगतान करें।",
                "notification_type": NotificationType.GENERAL,
                "is_banner": False,
            },
        ]
        
        for notif_data in notifications_data:
            notification = Notification(
                priority=2,
                utility_type="all",
                display_on_home=True,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(days=7),
                created_by=admin.id,
                **notif_data
            )
            db.add(notification)
        
        await db.commit()
        print("✅ Database seeded successfully!")
        print("\n📋 Demo Credentials:")
        print("  User Mobile: 9876543210 (Demo OTP will be shown)")
        print("  Admin: admin / admin123")
        print("  Operator: operator / operator123")


if __name__ == "__main__":
    asyncio.run(seed_database())
