import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { billsAPI } from '../services/api';

export default function Bills() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { state: { redirect: '/bills' } });
      return;
    }
    
    fetchBills();
  }, [isAuthenticated]);

  const fetchBills = async () => {
    try {
      const res = await billsAPI.getBills();
      setBills(res.data.bills || []);
    } catch (err) {
      console.error('Failed to fetch bills:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status, isOverdue) => {
    if (isOverdue) return 'var(--color-error)';
    switch (status) {
      case 'PAID': return 'var(--color-accent)';
      case 'PENDING': return 'var(--color-warning)';
      case 'PARTIALLY_PAID': return 'var(--color-info)';
      default: return 'var(--text-muted)';
    }
  };

  const getUtilityIcon = (type) => {
    switch (type) {
      case 'ELECTRICITY': return '⚡';
      case 'GAS': return '🔥';
      case 'WATER': return '💧';
      default: return '📄';
    }
  };

  const filteredBills = bills.filter(bill => {
    if (filter === 'all') return true;
    if (filter === 'pending') return ['PENDING', 'PARTIALLY_PAID', 'OVERDUE'].includes(bill.status);
    return bill.utility_type === filter.toUpperCase();
  });

  if (loading) {
    return (
      <div className="loading-overlay">
        <div className="loading-spinner"></div>
        <p style={{ marginTop: 'var(--space-md)' }}>{t('loading')}</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xl)' }}>
        <h1>{t('view_bills')}</h1>
        <button className="btn btn-secondary" onClick={() => navigate('/')}>
          {t('back')}
        </button>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 'var(--space-sm)', marginBottom: 'var(--space-xl)', flexWrap: 'wrap' }}>
        {['all', 'pending', 'electricity', 'gas', 'water'].map(f => (
          <button
            key={f}
            className={`btn ${filter === f ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFilter(f)}
            style={{ textTransform: 'capitalize' }}
          >
            {t(f) || f}
          </button>
        ))}
      </div>

      {/* Bills List */}
      {filteredBills.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
          <p style={{ color: 'var(--text-muted)' }}>No bills found</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {filteredBills.map(bill => (
            <div key={bill.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)' }}>
                <span style={{ fontSize: '2rem' }}>
                  {getUtilityIcon(bill.utility_type)}
                </span>
                <div>
                  <h3 style={{ margin: 0 }}>{t(bill.utility_type.toLowerCase())} Bill</h3>
                  <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
                    {bill.bill_number} • {t('due_date')}: {new Date(bill.due_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: '700', fontSize: 'var(--font-size-xl)' }}>
                  ₹{bill.outstanding_amount.toLocaleString()}
                </div>
                <div style={{
                  display: 'inline-block',
                  padding: '0.25rem 0.75rem',
                  borderRadius: 'var(--radius-md)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: '600',
                  backgroundColor: `${getStatusColor(bill.status, bill.is_overdue)}20`,
                  color: getStatusColor(bill.status, bill.is_overdue)
                }}>
                  {bill.is_overdue ? 'OVERDUE' : bill.status}
                </div>
                
                {bill.status !== 'PAID' && (
                  <button
                    className="btn btn-primary"
                    style={{ marginLeft: 'var(--space-md)' }}
                    onClick={() => navigate(`/bills/pay/${bill.id}`)}
                  >
                    {t('pay_now')}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
