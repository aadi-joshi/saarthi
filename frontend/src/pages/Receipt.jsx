import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { QRCodeSVG } from 'qrcode.react';

export default function Receipt() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { type, id } = useParams();
    const location = useLocation();
    const receipt = location.state?.receipt;

    if (!receipt) {
        return (
            <div className="card" style={{ textAlign: 'center', maxWidth: '500px', margin: '0 auto' }}>
                <h2>{t('error')}</h2>
                <p>Receipt data not found</p>
                <button className="btn btn-primary" onClick={() => navigate('/')}>
                    {t('home')}
                </button>
            </div>
        );
    }

    const handlePrint = () => {
        window.print();
    };

    return (
        <div style={{ maxWidth: '500px', margin: '0 auto' }}>
            {/* Success Header */}
            <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
                <div style={{
                    fontSize: '5rem',
                    marginBottom: 'var(--space-md)',
                    animation: 'pulse 1s ease'
                }}>
                    ✅
                </div>
                <h1 style={{ color: 'var(--color-accent)' }}>{t('payment_success')}</h1>
            </div>

            {/* Receipt Card */}
            <div className="receipt">
                <div className="receipt-header">
                    <h2>SUVIDHA</h2>
                    <p style={{ color: 'var(--text-muted)', margin: 0 }}>Payment Receipt</p>
                </div>

                {/* QR Code */}
                <div className="receipt-qr">
                    <QRCodeSVG
                        value={`SUVIDHA|${receipt.receipt_number}|${receipt.transaction_id}|${receipt.amount}`}
                        size={150}
                        level="H"
                    />
                </div>

                {/* Receipt Details */}
                <div className="receipt-details">
                    <div className="receipt-row">
                        <span>{t('transaction_id')}</span>
                        <strong>{receipt.transaction_id}</strong>
                    </div>
                    <div className="receipt-row">
                        <span>{t('receipt_number')}</span>
                        <strong>{receipt.receipt_number}</strong>
                    </div>
                    <div className="receipt-row">
                        <span>Date & Time</span>
                        <strong>{new Date(receipt.payment_time).toLocaleString()}</strong>
                    </div>
                    <div className="receipt-row">
                        <span>{t('bill_amount')}</span>
                        <strong style={{ fontSize: 'var(--font-size-xl)', color: 'var(--color-primary)' }}>
                            ₹{receipt.amount?.toLocaleString()}
                        </strong>
                    </div>
                </div>

                <div style={{
                    marginTop: 'var(--space-lg)',
                    padding: 'var(--space-md)',
                    background: 'var(--color-gray-100)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-muted)'
                }}>
                    {receipt.message || 'Thank you for your payment. This receipt can be used for future reference.'}
                </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: 'var(--space-md)', marginTop: 'var(--space-xl)' }}>
                <button className="btn btn-secondary btn-block" onClick={handlePrint}>
                    🖨️ {t('print')}
                </button>
                <button className="btn btn-primary btn-block" onClick={() => navigate('/')}>
                    {t('home')}
                </button>
            </div>

            <p style={{
                textAlign: 'center',
                marginTop: 'var(--space-xl)',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--text-muted)'
            }}>
                A copy of this receipt has been sent to your registered mobile number.
            </p>
        </div>
    );
}
