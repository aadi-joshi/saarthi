import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { grievancesAPI } from '../services/api';

export default function GrievanceTrack() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [trackingId, setTrackingId] = useState(location.state?.trackingId || '');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (location.state?.trackingId) {
      handleTrack();
    }
  }, []);

  const handleTrack = async () => {
    if (!trackingId) {
      setError('Please enter a tracking ID');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const res = await grievancesAPI.track(trackingId.toUpperCase());
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Grievance not found. Please check tracking ID.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'RESOLVED':
      case 'CLOSED':
        return 'var(--color-accent)';
      case 'IN_PROGRESS':
        return 'var(--color-info)';
      case 'ESCALATED':
        return 'var(--color-warning)';
      case 'REJECTED':
        return 'var(--color-error)';
      default:
        return 'var(--color-primary)';
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: 'var(--space-xl)' }}>{t('track_status')}</h1>

      {/* Search Form */}
      <div className="card" style={{ marginBottom: 'var(--space-xl)' }}>
        <div className="form-group">
          <label className="form-label">{t('tracking_id')}</label>
          <input
            type="text"
            className="form-input"
            value={trackingId}
            onChange={(e) => setTrackingId(e.target.value.toUpperCase())}
            placeholder="GRV-XXXXXX"
            style={{ textTransform: 'uppercase' }}
          />
        </div>
        <button
          className="btn btn-primary btn-block"
          onClick={handleTrack}
          disabled={loading}
        >
          {loading ? t('loading') : t('track_status')}
        </button>
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

      {/* Results */}
      {result && (
        <div className="card">
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 'var(--space-xl)'
          }}>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
                {t('tracking_id')}
              </div>
              <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: '700' }}>
                {result.tracking_id}
              </div>
            </div>
            <div style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: `${getStatusColor(result.status)}20`,
              color: getStatusColor(result.status),
              borderRadius: 'var(--radius-md)',
              fontWeight: '600'
            }}>
              {result.status}
            </div>
          </div>

          <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-xl)' }}>
            {result.status_description}
          </p>

          {/* Timeline */}
          <h3 style={{ marginBottom: 'var(--space-lg)' }}>Timeline</h3>
          <div style={{ position: 'relative', paddingLeft: 'var(--space-xl)' }}>
            {result.timeline?.map((step, index) => (
              <div
                key={index}
                style={{
                  position: 'relative',
                  paddingBottom: 'var(--space-lg)',
                  borderLeft: index < result.timeline.length - 1 
                    ? `2px solid ${step.completed ? 'var(--color-accent)' : 'var(--color-gray-300)'}`
                    : 'none',
                  marginLeft: '-1px'
                }}
              >
                <div style={{
                  position: 'absolute',
                  left: '-11px',
                  top: '0',
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  background: step.completed ? 'var(--color-accent)' : 'var(--color-gray-300)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem'
                }}>
                  {step.completed ? '✓' : (index + 1)}
                </div>
                <div style={{ paddingLeft: 'var(--space-lg)' }}>
                  <div style={{ fontWeight: '600' }}>{step.status}</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
                    {step.description}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-xs)' }}>
                    {new Date(step.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {result.expected_resolution && (
            <div style={{
              marginTop: 'var(--space-lg)',
              padding: 'var(--space-md)',
              background: 'var(--color-gray-100)',
              borderRadius: 'var(--radius-md)'
            }}>
              <strong>Expected Resolution:</strong>{' '}
              {new Date(result.expected_resolution).toLocaleDateString()}
            </div>
          )}
        </div>
      )}

      <button
        className="btn btn-secondary"
        onClick={() => navigate('/')}
        style={{ marginTop: 'var(--space-lg)', width: '100%' }}
      >
        {t('back')} {t('home')}
      </button>
    </div>
  );
}
