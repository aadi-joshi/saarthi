import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { connectionsAPI } from '../services/api';

const connectionTypes = [
    { value: 'ELECTRICITY_DOMESTIC', label: 'Electricity - Domestic', fee: 2100 },
    { value: 'ELECTRICITY_COMMERCIAL', label: 'Electricity - Commercial', fee: 7500 },
    { value: 'GAS_DOMESTIC', label: 'Gas - Domestic (PNG)', fee: 2600 },
    { value: 'GAS_COMMERCIAL', label: 'Gas - Commercial', fee: 10500 },
    { value: 'WATER_DOMESTIC', label: 'Water - Domestic', fee: 1350 },
    { value: 'WATER_COMMERCIAL', label: 'Water - Commercial', fee: 4200 },
];

export default function Connection() {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();

    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        connection_type: '',
        load_requirement: '',
        purpose: '',
        applicant_name: '',
        applicant_mobile: '',
        applicant_email: '',
        property_type: 'RESIDENTIAL',
        property_address: '',
        property_landmark: '',
        property_pin: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(null);

    const selectedType = connectionTypes.find(t => t.value === formData.connection_type);

    const validateStep = () => {
        if (step === 1 && !formData.connection_type) {
            setError('Please select a connection type');
            return false;
        }
        if (step === 2) {
            if (!formData.applicant_name || !formData.applicant_mobile) {
                setError(t('required_field'));
                return false;
            }
            if (!/^[6-9]\d{9}$/.test(formData.applicant_mobile)) {
                setError(t('invalid_mobile'));
                return false;
            }
        }
        if (step === 3) {
            if (!formData.property_address || !formData.property_pin) {
                setError(t('required_field'));
                return false;
            }
        }
        setError('');
        return true;
    };

    const handleNext = () => {
        if (validateStep()) {
            if (!isAuthenticated && step === 1) {
                navigate('/login', { state: { redirect: '/connection' } });
                return;
            }
            setStep(prev => prev + 1);
        }
    };

    const handleSubmit = async () => {
        if (!validateStep()) return;

        setLoading(true);
        try {
            const res = await connectionsAPI.apply(formData);
            setSuccess({
                applicationNumber: res.data.application_number,
                totalFee: res.data.total_fee,
            });
            setStep(4);
        } catch (err) {
            setError(err.response?.data?.detail || t('network_error'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: 'var(--space-xl)' }}>{t('new_connection')}</h1>

            {/* Step Indicator */}
            <div className="step-indicator">
                {[1, 2, 3].map(s => (
                    <>
                        <div key={s} className={`step ${step === s ? 'active' : step > s ? 'completed' : ''}`}>
                            <span className="step-number">{step > s ? '✓' : s}</span>
                        </div>
                        {s < 3 && <div className={`step-connector ${step > s ? 'completed' : ''}`}></div>}
                    </>
                ))}
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

            {/* Step 1: Connection Type */}
            {step === 1 && (
                <div className="card">
                    <h3 style={{ marginBottom: 'var(--space-lg)' }}>Select Connection Type</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                        {connectionTypes.map(type => (
                            <label
                                key={type.value}
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: 'var(--space-md)',
                                    border: `2px solid ${formData.connection_type === type.value ? 'var(--color-primary)' : 'var(--color-gray-200)'}`,
                                    borderRadius: 'var(--radius-md)',
                                    cursor: 'pointer',
                                    backgroundColor: formData.connection_type === type.value ? 'var(--color-gray-50)' : 'transparent'
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                                    <input
                                        type="radio"
                                        name="connectionType"
                                        value={type.value}
                                        checked={formData.connection_type === type.value}
                                        onChange={(e) => setFormData({ ...formData, connection_type: e.target.value })}
                                    />
                                    <span>{type.label}</span>
                                </div>
                                <span style={{ fontWeight: '600' }}>₹{type.fee.toLocaleString()}</span>
                            </label>
                        ))}
                    </div>
                </div>
            )}

            {/* Step 2: Applicant Details */}
            {step === 2 && (
                <div className="card">
                    <h3 style={{ marginBottom: 'var(--space-lg)' }}>Applicant Details</h3>

                    <div className="form-group">
                        <label className="form-label">{t('applicant_name')} *</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.applicant_name}
                            onChange={(e) => setFormData({ ...formData, applicant_name: e.target.value })}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Mobile Number *</label>
                        <input
                            type="tel"
                            className="form-input"
                            value={formData.applicant_mobile}
                            onChange={(e) => setFormData({ ...formData, applicant_mobile: e.target.value.replace(/\D/g, '').slice(0, 10) })}
                            maxLength={10}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Email</label>
                        <input
                            type="email"
                            className="form-input"
                            value={formData.applicant_email}
                            onChange={(e) => setFormData({ ...formData, applicant_email: e.target.value })}
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Load Requirement (if applicable)</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.load_requirement}
                            onChange={(e) => setFormData({ ...formData, load_requirement: e.target.value })}
                            placeholder="e.g., 5 KW"
                        />
                    </div>
                </div>
            )}

            {/* Step 3: Property Details */}
            {step === 3 && (
                <div className="card">
                    <h3 style={{ marginBottom: 'var(--space-lg)' }}>Property Details</h3>

                    <div className="form-group">
                        <label className="form-label">Property Type</label>
                        <select
                            className="form-input"
                            value={formData.property_type}
                            onChange={(e) => setFormData({ ...formData, property_type: e.target.value })}
                        >
                            <option value="RESIDENTIAL">Residential</option>
                            <option value="COMMERCIAL">Commercial</option>
                            <option value="INDUSTRIAL">Industrial</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="form-label">{t('property_address')} *</label>
                        <textarea
                            className="form-input"
                            value={formData.property_address}
                            onChange={(e) => setFormData({ ...formData, property_address: e.target.value })}
                            rows={3}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Landmark</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.property_landmark}
                            onChange={(e) => setFormData({ ...formData, property_landmark: e.target.value })}
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">PIN Code *</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.property_pin}
                            onChange={(e) => setFormData({ ...formData, property_pin: e.target.value.replace(/\D/g, '').slice(0, 6) })}
                            maxLength={6}
                            required
                        />
                    </div>

                    {/* Fee Summary */}
                    <div style={{
                        marginTop: 'var(--space-lg)',
                        padding: 'var(--space-lg)',
                        background: 'var(--color-gray-100)',
                        borderRadius: 'var(--radius-md)'
                    }}>
                        <h4 style={{ marginBottom: 'var(--space-md)' }}>Fee Summary</h4>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>{t('application_fee')}</span>
                            <span>₹{selectedType?.fee ? Math.round(selectedType.fee * 0.05) : 0}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Connection Fee</span>
                            <span>₹{selectedType?.fee ? Math.round(selectedType.fee * 0.7) : 0}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Security Deposit</span>
                            <span>₹{selectedType?.fee ? Math.round(selectedType.fee * 0.25) : 0}</span>
                        </div>
                        <hr style={{ margin: 'var(--space-sm) 0', border: 'none', borderTop: '1px solid var(--color-gray-300)' }} />
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: '700' }}>
                            <span>Total</span>
                            <span>₹{selectedType?.fee?.toLocaleString() || 0}</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Step 4: Success */}
            {step === 4 && success && (
                <div className="card" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '4rem', marginBottom: 'var(--space-lg)' }}>✅</div>
                    <h2>Application Submitted</h2>
                    <p style={{ marginBottom: 'var(--space-xl)' }}>
                        Your connection request has been submitted successfully.
                    </p>

                    <div style={{
                        padding: 'var(--space-lg)',
                        background: 'var(--color-gray-100)',
                        borderRadius: 'var(--radius-lg)',
                        marginBottom: 'var(--space-xl)'
                    }}>
                        <p style={{ marginBottom: 'var(--space-sm)', color: 'var(--text-muted)' }}>
                            Application Number
                        </p>
                        <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: '700', color: 'var(--color-primary)' }}>
                            {success.applicationNumber}
                        </div>
                    </div>

                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
                        Next Steps: Upload required documents and pay the application fee.
                    </p>

                    <button className="btn btn-primary btn-block" onClick={() => navigate('/')}>
                        {t('home')}
                    </button>
                </div>
            )}

            {/* Navigation Buttons */}
            {step < 4 && (
                <div style={{ display: 'flex', gap: 'var(--space-md)', marginTop: 'var(--space-xl)' }}>
                    {step > 1 ? (
                        <button className="btn btn-secondary" onClick={() => setStep(prev => prev - 1)}>
                            {t('back')}
                        </button>
                    ) : (
                        <button className="btn btn-secondary" onClick={() => navigate('/')}>
                            {t('cancel')}
                        </button>
                    )}

                    {step < 3 ? (
                        <button className="btn btn-primary btn-block btn-large" onClick={handleNext} disabled={loading}>
                            {t('continue')}
                        </button>
                    ) : (
                        <button className="btn btn-primary btn-block btn-large" onClick={handleSubmit} disabled={loading}>
                            {loading ? t('loading') : t('submit')}
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
