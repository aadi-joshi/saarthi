import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

export default function Login() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();
    const { login } = useAuth();

    const [step, setStep] = useState('mobile'); // mobile, otp
    const [mobile, setMobile] = useState('');
    const [otp, setOtp] = useState('');
    const [demoOtp, setDemoOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSendOTP = async (e) => {
        e.preventDefault();
        setError('');

        // Validate mobile
        if (!/^[6-9]\d{9}$/.test(mobile)) {
            setError(t('invalid_mobile'));
            return;
        }

        setLoading(true);
        try {
            const res = await authAPI.requestOTP(mobile);
            if (res.data.demo_otp) {
                setDemoOtp(res.data.demo_otp); // For demo purposes
            }
            setStep('otp');
        } catch (err) {
            setError(err.response?.data?.detail || t('network_error'));
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyOTP = async (e) => {
        e.preventDefault();
        setError('');

        if (otp.length !== 6) {
            setError(t('invalid_otp'));
            return;
        }

        setLoading(true);
        try {
            const res = await authAPI.verifyOTP(mobile, otp);
            await login(
                res.data.access_token,
                res.data.refresh_token,
                { id: res.data.user_id, mobile }
            );

            // Redirect to intended page or home
            const redirect = location.state?.redirect || '/';
            navigate(redirect);
        } catch (err) {
            setError(err.response?.data?.detail || t('invalid_otp'));
        } finally {
            setLoading(false);
        }
    };

    const handleBack = () => {
        setStep('mobile');
        setOtp('');
        setError('');
    };

    return (
        <div style={{ maxWidth: '400px', margin: '0 auto' }}>
            <div className="card">
                <div className="card-header">
                    <h2 className="card-title">{t('login')}</h2>
                </div>

                {/* Step Indicator */}
                <div className="step-indicator">
                    <div className={`step ${step === 'mobile' ? 'active' : 'completed'}`}>
                        <span className="step-number">1</span>
                        <span className="step-label">{t('enter_mobile')}</span>
                    </div>
                    <div className="step-connector"></div>
                    <div className={`step ${step === 'otp' ? 'active' : ''}`}>
                        <span className="step-number">2</span>
                        <span className="step-label">{t('verify_otp')}</span>
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

                {step === 'mobile' ? (
                    <form onSubmit={handleSendOTP}>
                        <div className="form-group">
                            <label className="form-label">{t('enter_mobile')}</label>
                            <input
                                type="tel"
                                className="form-input"
                                value={mobile}
                                onChange={(e) => setMobile(e.target.value.replace(/\D/g, '').slice(0, 10))}
                                placeholder="9876543210"
                                maxLength={10}
                                autoFocus
                            />
                        </div>
                        <button
                            type="submit"
                            className="btn btn-primary btn-block btn-large"
                            disabled={loading || mobile.length !== 10}
                        >
                            {loading ? t('loading') : t('send_otp')}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOTP}>
                        <div className="form-group">
                            <label className="form-label">{t('enter_otp')}</label>
                            <input
                                type="tel"
                                className="form-input"
                                value={otp}
                                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                placeholder="000000"
                                maxLength={6}
                                autoFocus
                                style={{ letterSpacing: '1rem', textAlign: 'center', fontSize: '1.5rem' }}
                            />
                            {demoOtp && (
                                <p style={{ marginTop: 'var(--space-sm)', color: 'var(--color-info)', fontSize: 'var(--font-size-sm)' }}>
                                    Demo OTP: <strong>{demoOtp}</strong>
                                </p>
                            )}
                        </div>

                        <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={handleBack}
                            >
                                {t('back')}
                            </button>
                            <button
                                type="submit"
                                className="btn btn-primary btn-block btn-large"
                                disabled={loading || otp.length !== 6}
                            >
                                {loading ? t('loading') : t('verify_otp')}
                            </button>
                        </div>

                        <button
                            type="button"
                            style={{
                                marginTop: 'var(--space-lg)',
                                background: 'none',
                                border: 'none',
                                color: 'var(--color-primary)',
                                cursor: 'pointer'
                            }}
                            onClick={handleSendOTP}
                        >
                            {t('resend_otp')}
                        </button>
                    </form>
                )}
            </div>

            <button
                onClick={() => navigate('/')}
                className="btn btn-secondary"
                style={{ marginTop: 'var(--space-lg)', width: '100%' }}
            >
                {t('back')} {t('home')}
            </button>
        </div>
    );
}
