import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { grievancesAPI } from '../services/api';

const categories = [
    { value: 'POWER_OUTAGE', label: 'Power Outage', label_hi: 'बिजली कटौती' },
    { value: 'GAS_LEAK', label: 'Gas Leak (Emergency)', label_hi: 'गैस रिसाव (आपातकाल)' },
    { value: 'WATER_SUPPLY', label: 'Water Supply Issue', label_hi: 'पानी आपूर्ति समस्या' },
    { value: 'BILLING_DISPUTE', label: 'Billing Dispute', label_hi: 'बिलिंग विवाद' },
    { value: 'METER_ISSUE', label: 'Meter Issue', label_hi: 'मीटर समस्या' },
    { value: 'STREET_LIGHT', label: 'Street Light', label_hi: 'स्ट्रीट लाइट' },
    { value: 'GARBAGE_COLLECTION', label: 'Garbage Collection', label_hi: 'कचरा संग्रह' },
    { value: 'SEWERAGE', label: 'Sewerage', label_hi: 'सीवरेज' },
    { value: 'OTHER', label: 'Other', label_hi: 'अन्य' },
];

export default function Grievance() {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();

    const [formData, setFormData] = useState({
        category: '',
        subject: '',
        description: '',
        location_address: '',
        location_pin: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validate
        if (!formData.category || !formData.subject || !formData.description) {
            setError(t('required_field'));
            return;
        }

        // Check auth for non-emergency
        if (!isAuthenticated && formData.category !== 'GAS_LEAK') {
            navigate('/login', { state: { redirect: '/grievance' } });
            return;
        }

        setLoading(true);
        try {
            const res = await grievancesAPI.create(formData);
            setSuccess({
                trackingId: res.data.tracking_id,
                category: res.data.category,
            });
        } catch (err) {
            setError(err.response?.data?.detail || t('network_error'));
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="card" style={{ maxWidth: '500px', margin: '0 auto', textAlign: 'center' }}>
                <div style={{ fontSize: '4rem', marginBottom: 'var(--space-lg)' }}>✅</div>
                <h2>{t('complaint_registered')}</h2>
                <p style={{ marginBottom: 'var(--space-xl)' }}>
                    Your complaint has been successfully registered.
                </p>

                <div style={{
                    padding: 'var(--space-lg)',
                    background: 'var(--color-gray-100)',
                    borderRadius: 'var(--radius-lg)',
                    marginBottom: 'var(--space-xl)'
                }}>
                    <p style={{ marginBottom: 'var(--space-sm)', color: 'var(--text-muted)' }}>
                        {t('tracking_id')}
                    </p>
                    <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: '700', color: 'var(--color-primary)' }}>
                        {success.trackingId}
                    </div>
                </div>

                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
                    Please save this tracking ID to check the status of your complaint.
                </p>

                <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                    <button className="btn btn-secondary btn-block" onClick={() => navigate('/')}>
                        {t('home')}
                    </button>
                    <button
                        className="btn btn-primary btn-block"
                        onClick={() => navigate('/grievance/track', { state: { trackingId: success.trackingId } })}
                    >
                        {t('track_status')}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: 'var(--space-xl)' }}>{t('file_complaint')}</h1>

            {/* Emergency Warning */}
            {formData.category === 'GAS_LEAK' && (
                <div style={{
                    padding: 'var(--space-md)',
                    background: '#FED7D7',
                    color: '#C53030',
                    borderRadius: 'var(--radius-md)',
                    marginBottom: 'var(--space-lg)',
                    fontWeight: '600'
                }}>
                    ⚠️ This is an EMERGENCY. If you smell gas, please also call 1906 immediately!
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div className="card">
                    {/* Category */}
                    <div className="form-group">
                        <label className="form-label">{t('category')} *</label>
                        <select
                            className="form-input"
                            value={formData.category}
                            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                            required
                        >
                            <option value="">Select category</option>
                            {categories.map(cat => (
                                <option key={cat.value} value={cat.value}>
                                    {i18n.language === 'hi' ? cat.label_hi : cat.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Subject */}
                    <div className="form-group">
                        <label className="form-label">{t('subject')} *</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.subject}
                            onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                            placeholder="Brief description of the issue"
                            required
                        />
                    </div>

                    {/* Description */}
                    <div className="form-group">
                        <label className="form-label">{t('description')} *</label>
                        <textarea
                            className="form-input"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Provide detailed information about your complaint"
                            rows={4}
                            style={{ resize: 'vertical' }}
                            required
                        />
                    </div>

                    {/* Location */}
                    <div className="form-group">
                        <label className="form-label">{t('location')}</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.location_address}
                            onChange={(e) => setFormData({ ...formData, location_address: e.target.value })}
                            placeholder="Address where the issue is located"
                        />
                    </div>

                    {/* PIN Code */}
                    <div className="form-group">
                        <label className="form-label">PIN Code</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.location_pin}
                            onChange={(e) => setFormData({ ...formData, location_pin: e.target.value.replace(/\D/g, '').slice(0, 6) })}
                            placeholder="6-digit PIN code"
                            maxLength={6}
                        />
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

                    <div style={{ display: 'flex', gap: 'var(--space-md)', marginTop: 'var(--space-lg)' }}>
                        <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={() => navigate('/')}
                        >
                            {t('cancel')}
                        </button>
                        <button
                            type="submit"
                            className="btn btn-primary btn-block btn-large"
                            disabled={loading}
                        >
                            {loading ? t('loading') : t('submit')}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}
