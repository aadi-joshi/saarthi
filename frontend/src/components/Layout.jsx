import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSession } from '../context/SessionContext';
import { useAccessibility } from '../context/AccessibilityContext';

export default function Layout() {
    const { t, i18n } = useTranslation();
    const { showWarning, timeRemaining, extendSession } = useSession();
    const { highContrast, elderlyMode, toggleHighContrast, toggleElderlyMode } = useAccessibility();
    const [isOnline, setIsOnline] = useState(navigator.onLine);
    const [showAccessibility, setShowAccessibility] = useState(false);

    // Track online status
    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    const changeLanguage = (lang) => {
        i18n.changeLanguage(lang);
    };

    return (
        <div className="kiosk-container">
            {/* Offline Banner */}
            {!isOnline && (
                <div className="offline-banner">
                    <span className="offline-dot"></span>
                    <span>{t('offline_message')}</span>
                </div>
            )}

            {/* Header */}
            <header className="kiosk-header">
                <div className="kiosk-logo">
                    <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                        <circle cx="24" cy="24" r="22" stroke="currentColor" strokeWidth="2" />
                        <text x="24" y="30" textAnchor="middle" fill="currentColor" fontSize="16" fontWeight="bold">S</text>
                    </svg>
                    <div>
                        <div className="kiosk-logo-text">{t('app_name')}</div>
                        <div style={{ fontSize: '0.875rem', opacity: 0.8 }}>{t('app_subtitle')}</div>
                    </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    {/* Language Toggle */}
                    <div className="language-toggle">
                        <button
                            className={i18n.language === 'en' ? 'active' : ''}
                            onClick={() => changeLanguage('en')}
                        >
                            English
                        </button>
                        <button
                            className={i18n.language === 'hi' ? 'active' : ''}
                            onClick={() => changeLanguage('hi')}
                        >
                            हिंदी
                        </button>
                    </div>

                    {/* Accessibility Toggle */}
                    <button
                        onClick={() => setShowAccessibility(!showAccessibility)}
                        style={{
                            background: 'rgba(255,255,255,0.1)',
                            border: 'none',
                            padding: '0.5rem 1rem',
                            borderRadius: '0.5rem',
                            color: 'white',
                            cursor: 'pointer'
                        }}
                    >
                        ♿ {t('accessibility')}
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="kiosk-main">
                <Outlet />
            </main>

            {/* Footer */}
            <footer className="kiosk-footer">
                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    © 2026 {t('app_name')} - C-DAC Hackathon
                </div>
                <div style={{ display: 'flex', gap: '1.5rem' }}>
                    <button style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                        {t('help')}
                    </button>
                    <button style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                        {t('contact')}
                    </button>
                </div>
            </footer>

            {/* Session Timeout Warning */}
            {showWarning && (
                <div className="modal-overlay">
                    <div className="modal">
                        <h2 className="modal-title">{t('session_timeout')}</h2>
                        <p>
                            {t('session_warning')} <strong>{timeRemaining}</strong> {t('seconds')}.
                        </p>
                        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem' }}>
                            <button className="btn btn-primary btn-block" onClick={extendSession}>
                                {t('extend_session')}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Accessibility Panel */}
            {showAccessibility && (
                <div className="accessibility-panel">
                    <h3 style={{ marginBottom: '1rem' }}>{t('accessibility')}</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <button
                            className={`accessibility-btn ${highContrast ? 'active' : ''}`}
                            onClick={toggleHighContrast}
                        >
                            🔲 {t('high_contrast')}
                        </button>
                        <button
                            className={`accessibility-btn ${elderlyMode ? 'active' : ''}`}
                            onClick={toggleElderlyMode}
                        >
                            👴 {t('elderly_mode')}
                        </button>
                    </div>
                    <button
                        onClick={() => setShowAccessibility(false)}
                        style={{
                            marginTop: '1rem',
                            width: '100%',
                            padding: '0.5rem',
                            background: 'var(--color-gray-100)',
                            border: 'none',
                            borderRadius: '0.5rem',
                            cursor: 'pointer'
                        }}
                    >
                        {t('close')}
                    </button>
                </div>
            )}
        </div>
    );
}
