import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { billsAPI } from '../services/api';

export default function BillPayment() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { id } = useParams();

    const [bill, setBill] = useState(null);
    const [loading, setLoading] = useState(true);
    const [paying, setPaying] = useState(false);
    const [paymentMethod, setPaymentMethod] = useState('UPI');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchBill();
    }, [id]);

    const fetchBill = async () => {
        try {
            const res = await billsAPI.getBill(id);
            setBill(res.data);
        } catch (err) {
            setError('Bill not found');
        } finally {
            setLoading(false);
        }
    };

    const handlePayment = async () => {
        setPaying(true);
        setError('');

        try {
            const res = await billsAPI.payBill({
                bill_id: parseInt(id),
                amount: bill.outstanding_amount,
                payment_method: paymentMethod
            });

            // Navigate to receipt
            navigate(`/receipt/payment/${res.data.transaction_id}`, {
                state: { receipt: res.data }
            });
        } catch (err) {
            setError(err.response?.data?.detail || t('payment_failed'));
            setPaying(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    if (error && !bill) {
        return (
            <div className="card" style={{ textAlign: 'center', maxWidth: '500px', margin: '0 auto' }}>
                <h2>{t('error')}</h2>
                <p>{error}</p>
                <button className="btn btn-primary" onClick={() => navigate('/bills')}>
                    {t('back')}
                </button>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: 'var(--space-xl)' }}>{t('bill_payment')}</h1>

            {/* Bill Summary */}
            <div className="card" style={{ marginBottom: 'var(--space-xl)' }}>
                <div className="card-header">
                    <h3 className="card-title">Bill Summary</h3>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{t('bill_number')}</span>
                        <strong>{bill.bill_number}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Utility Type</span>
                        <strong>{bill.utility_type}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{t('due_date')}</span>
                        <strong>{new Date(bill.due_date).toLocaleDateString()}</strong>
                    </div>
                    <hr style={{ border: 'none', borderTop: '1px solid var(--color-gray-200)', margin: 'var(--space-md) 0' }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Total Amount</span>
                        <span>₹{bill.total_amount.toLocaleString()}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Already Paid</span>
                        <span>₹{bill.amount_paid.toLocaleString()}</span>
                    </div>
                    <hr style={{ border: 'none', borderTop: '1px solid var(--color-gray-200)', margin: 'var(--space-md) 0' }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-xl)', fontWeight: '700' }}>
                        <span>Amount to Pay</span>
                        <span style={{ color: 'var(--color-primary)' }}>₹{bill.outstanding_amount.toLocaleString()}</span>
                    </div>
                </div>
            </div>

            {/* Payment Method */}
            <div className="card" style={{ marginBottom: 'var(--space-xl)' }}>
                <div className="card-header">
                    <h3 className="card-title">{t('payment_method')}</h3>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                    {[
                        { id: 'UPI', label: 'UPI / BHIM', icon: '📱' },
                        { id: 'CARD', label: 'Credit/Debit Card', icon: '💳' },
                        { id: 'NETBANKING', label: 'Net Banking', icon: '🏦' },
                        { id: 'CASH', label: 'Cash (Kiosk)', icon: '💵' },
                    ].map(method => (
                        <label
                            key={method.id}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--space-md)',
                                padding: 'var(--space-md)',
                                border: `2px solid ${paymentMethod === method.id ? 'var(--color-primary)' : 'var(--color-gray-200)'}`,
                                borderRadius: 'var(--radius-md)',
                                cursor: 'pointer',
                                backgroundColor: paymentMethod === method.id ? 'var(--color-gray-50)' : 'transparent'
                            }}
                        >
                            <input
                                type="radio"
                                name="paymentMethod"
                                value={method.id}
                                checked={paymentMethod === method.id}
                                onChange={(e) => setPaymentMethod(e.target.value)}
                                style={{ width: '20px', height: '20px' }}
                            />
                            <span style={{ fontSize: '1.5rem' }}>{method.icon}</span>
                            <span>{method.label}</span>
                        </label>
                    ))}
                </div>
            </div>

            {error && (
                <div style={{
                    padding: 'var(--space-md)',
                    background: '#FED7D7',
                    color: '#C53030',
                    borderRadius: 'var(--radius-md)',
                    marginBottom: 'var(--space-lg)'
                }}>
                    {error}
                </div>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                <button
                    className="btn btn-secondary"
                    onClick={() => navigate('/bills')}
                    disabled={paying}
                >
                    {t('cancel')}
                </button>
                <button
                    className="btn btn-primary btn-block btn-large"
                    onClick={handlePayment}
                    disabled={paying}
                >
                    {paying ? t('loading') : `${t('pay_now')} ₹${bill.outstanding_amount.toLocaleString()}`}
                </button>
            </div>
        </div>
    );
}
