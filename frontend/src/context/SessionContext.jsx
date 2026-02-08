import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const SessionContext = createContext(null);

const SESSION_TIMEOUT = 10 * 60 * 1000; // 10 minutes
const WARNING_TIME = 60 * 1000; // 1 minute before timeout

export function SessionProvider({ children }) {
  const [lastActivity, setLastActivity] = useState(Date.now());
  const [showWarning, setShowWarning] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [sessionId, setSessionId] = useState(null);

  // Generate session ID on mount
  useEffect(() => {
    const id = `SES_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(id);
    
    // Start session in backend
    fetch('/api/v1/analytics/session/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        language: 'en',
        accessibility_mode: false,
        elderly_mode: false,
      }),
    }).catch(() => {});
    
    return () => {
      // End session on unmount
      if (sessionId) {
        fetch(`/api/v1/analytics/session/${sessionId}/end`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ended_by: 'navigation' }),
        }).catch(() => {});
      }
    };
  }, []);

  // Track activity
  const recordActivity = useCallback((page, action) => {
    setLastActivity(Date.now());
    setShowWarning(false);
    
    if (sessionId) {
      fetch(`/api/v1/analytics/session/${sessionId}/activity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ page, action }),
      }).catch(() => {});
    }
  }, [sessionId]);

  // Check timeout
  useEffect(() => {
    const interval = setInterval(() => {
      const elapsed = Date.now() - lastActivity;
      const remaining = SESSION_TIMEOUT - elapsed;
      
      if (remaining <= 0) {
        // Session expired - reset
        handleTimeout();
      } else if (remaining <= WARNING_TIME) {
        // Show warning
        setShowWarning(true);
        setTimeRemaining(Math.ceil(remaining / 1000));
      }
    }, 1000);
    
    return () => clearInterval(interval);
  }, [lastActivity]);

  // Reset on activity
  useEffect(() => {
    const handleActivity = () => {
      setLastActivity(Date.now());
      setShowWarning(false);
    };
    
    window.addEventListener('click', handleActivity);
    window.addEventListener('touchstart', handleActivity);
    window.addEventListener('keydown', handleActivity);
    
    return () => {
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('touchstart', handleActivity);
      window.removeEventListener('keydown', handleActivity);
    };
  }, []);

  const handleTimeout = () => {
    // Clear session and redirect to home
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  const extendSession = () => {
    setLastActivity(Date.now());
    setShowWarning(false);
  };

  const value = {
    sessionId,
    showWarning,
    timeRemaining,
    recordActivity,
    extendSession,
    handleTimeout,
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}
