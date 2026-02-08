import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { grievancesAPI, connectionsAPI } from '../services/api';

export default function Track() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [trackingType, setTrackingType] = useState('grievance');
  const [trackingId, setTrackingId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleTrack = async (e) => {
    e.preventDefault();
    if (!trackingId) {
      setError('Please enter a tracking/application number');
      return;
    }
    
    setLoading(true);
    setError('');
    setResult(null);
    
    try {
      let res;
      if (trackingType === 'grievance') {
        res = await grievancesAPI.track(trackingId.toUpperCase());
      } else {
        res = await connectionsAPI.track(trackingId.toUpperCase());
      }
      setResult({ type: trackingType, data: res.data });
    } catch (err) {
      setError(err.response?.data?.detail || 'Not found. Please check your ID.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower.includes('completed') || statusLower.includes('resolved') || statusLower.includes('closed')) {
      return 'var(--color-accent)';
    }
    if (statusLower.includes('progress') || statusLower.includes('approved')) {
      return 'var(--color-info)';
    }
    if (statusLower.includes('rejected') || statusLower.includes('cancelled')) {
      return 'var(--color-error)';
    }
    return 'var(--color-warning)';
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: 'var(--space-xl)' }}>{t('track_status')}</h1>

      {/* Type Selection */}
      <div className="card" style={{ marginBottom: 'var(--space-xl)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-md)', marginBottom: 'var(--space-lg)' }}>
          <button
            className={`btn ${trackingType === 'grievance' ? 'btn-primary' : 'btn-secondary'} btn-block`}
            onClick={() => { setTrackingType('grievance'); setResult(null); setError(''); }}
          >
            📝 Grievance
          </button>
          <button
            className={`btn ${trackingType === 'connection' ? 'btn-primary' : 'btn-secondary'} btn-block`}
            onClick={() => { setTrackingType('connection'); setResult(null); setError(''); }}
          >
            🔌 Connection
          </button>
        </div>

        <form onSubmit={handleTrack}>
          <div className="form-group">
            <label className="form-label">
              {trackingType === 'grievance' ? t('tracking_id') : 'Application Number'}
            </label>
            <input
              type="text"
              className="form-input"
              value={trackingId}
              onChange={(e) => setTrackingId(e.target.value.toUpperCase())}
              placeholder={trackingType === 'grievance' ? 'GRV-XXXXXX' : 'CON-XXXXXX'}
              style={{ textTransform: 'uppercase' }}
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary btn-block btn-large"
            disabled={loading}
          >
            {loading ? t('loading') : t('track_status')}
          </button>
        </form>
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

      {/* Grievance Result */}
      {result?.type === 'grievance' && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
            <h3>{result.data.tracking_id}</h3>
            <span style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: `${getStatusColor(result.data.status)}20`,
              color: getStatusColor(result.data.status),
              borderRadius: 'var(--radius-md)',
              fontWeight: '600'
            }}>
              {result.data.status}
            </span>
          </div>
          
          <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)' }}>
            {result.data.status_description}
          </p>

          {result.data.timeline?.length > 0 && (
            <>
              <h4>Timeline</h4>
              <div style={{ paddingLeft: 'var(--space-lg)', marginTop: 'var(--space-md)' }}>
                {result.data.timeline.map((step, i) => (
                  <div key={i} style={{
                    position: 'relative',
                    paddingBottom: 'var(--space-md)',
                    paddingLeft: 'var(--space-lg)',
                    borderLeft: i < result.data.timeline.length - 1 ? '2px solid var(--color-gray-300)' : 'none'
                  }}>
                    <div style={{
                      position: 'absolute',
                      left: '-8px',
                      width: '16px',
                      height: '16px',
                      borderRadius: '50%',
                      background: step.completed ? 'var(--color-accent)' : 'var(--color-gray-300)'
                    }} />
                    <strong>{step.status}</strong>
                    <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
                      {step.description}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Connection Result */}
      {result?.type === 'connection' && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
            <h3>{result.data.application_number}</h3>
            <span style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: `${getStatusColor(result.data.status)}20`,
              color: getStatusColor(result.data.status),
              borderRadius: 'var(--radius-md)',
              fontWeight: '600'
            }}>
              {result.data.status}
            </span>
          </div>

          <div style={{ marginBottom: 'var(--space-lg)' }}>
            <strong>Connection Type:</strong> {result.data.connection_type}
          </div>

          {/* Step Progress */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-lg)' }}>
            {result.data.steps?.map((step, i) => (
              <div key={i} style={{ textAlign: 'center', flex: 1 }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  margin: '0 auto var(--space-sm)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: step.completed ? 'var(--color-accent)' : 'var(--color-gray-300)',
                  color: 'white',
                  fontWeight: '600'
                }}>
                  {step.completed ? '✓' : step.step}
                </div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                  {step.name}
                </div>
              </div>
            ))}
          </div>

          <div style={{
            padding: 'var(--space-md)',
            background: 'var(--color-gray-100)',
            borderRadius: 'var(--radius-md)'
          }}>
            <strong>Expected Completion:</strong> {result.data.expected_completion}
          </div>
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
