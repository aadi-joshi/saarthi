import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { notificationsAPI } from '../services/api';

// Service icons (emoji for demo, replace with proper SVGs in production)
const services = [
  { id: 'electricity', icon: '⚡', color: '#f6ad55' },
  { id: 'gas', icon: '🔥', color: '#fc8181' },
  { id: 'water', icon: '💧', color: '#63b3ed' },
  { id: 'municipal', icon: '🏛️', color: '#68d391' },
];

const actions = [
  { id: 'pay_bill', icon: '💳', path: '/bills', requiresAuth: true },
  { id: 'file_complaint', icon: '📝', path: '/grievance', requiresAuth: false },
  { id: 'new_connection', icon: '🔌', path: '/connection', requiresAuth: true },
  { id: 'track_status', icon: '🔍', path: '/track', requiresAuth: false },
];

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [currentBanner, setCurrentBanner] = useState(0);

  useEffect(() => {
    // Fetch active notifications
    notificationsAPI.getActive()
      .then(res => {
        if (res.data.banner_notifications) {
          setNotifications(res.data.banner_notifications);
        }
      })
      .catch(() => {});
  }, []);

  // Rotate banners
  useEffect(() => {
    if (notifications.length > 1) {
      const interval = setInterval(() => {
        setCurrentBanner(prev => (prev + 1) % notifications.length);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [notifications.length]);

  const handleAction = (action) => {
    if (action.requiresAuth && !isAuthenticated) {
      navigate('/login', { state: { redirect: action.path } });
    } else {
      navigate(action.path);
    }
  };

  return (
    <div>
      {/* Banner Notifications */}
      {notifications.length > 0 && (
        <div className={`notification-banner ${notifications[currentBanner]?.notification_type === 'EMERGENCY' ? 'emergency' : ''}`}>
          {notifications[currentBanner]?.title}
        </div>
      )}

      {/* Welcome Message */}
      <div style={{ textAlign: 'center', marginBottom: 'var(--space-2xl)' }}>
        <h1>{t('welcome')}</h1>
        <p style={{ fontSize: 'var(--font-size-lg)', color: 'var(--text-secondary)' }}>
          {t('app_subtitle')}
        </p>
      </div>

      {/* Service Tiles */}
      <h2 style={{ marginBottom: 'var(--space-lg)' }}>{t('services')}</h2>
      <div className="service-grid">
        {services.map(service => (
          <div
            key={service.id}
            className="service-tile"
            onClick={() => handleAction(actions[0])}
            style={{ '--service-color': service.color }}
          >
            <span className="service-tile-icon" style={{ color: service.color }}>
              {service.icon}
            </span>
            <span className="service-tile-title">{t(service.id)}</span>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <h2 style={{ margin: 'var(--space-2xl) 0 var(--space-lg)' }}>Quick Actions</h2>
      <div className="service-grid">
        {actions.map(action => (
          <div
            key={action.id}
            className="service-tile"
            onClick={() => handleAction(action)}
          >
            <span className="service-tile-icon">{action.icon}</span>
            <span className="service-tile-title">{t(action.id)}</span>
            {action.requiresAuth && !isAuthenticated && (
              <span className="service-tile-subtitle">{t('login')} required</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
