import { createContext, useContext, useState, useEffect } from 'react';

const AccessibilityContext = createContext(null);

export function AccessibilityProvider({ children }) {
  const [highContrast, setHighContrast] = useState(false);
  const [elderlyMode, setElderlyMode] = useState(false);
  const [fontSize, setFontSize] = useState('normal'); // normal, large, extra-large

  useEffect(() => {
    // Apply high contrast mode
    document.documentElement.setAttribute(
      'data-contrast',
      highContrast ? 'high' : 'normal'
    );
  }, [highContrast]);

  useEffect(() => {
    // Apply elderly mode
    document.documentElement.setAttribute(
      'data-elderly',
      elderlyMode ? 'true' : 'false'
    );
  }, [elderlyMode]);

  useEffect(() => {
    // Apply font size
    const sizes = {
      normal: '16px',
      large: '20px',
      'extra-large': '24px',
    };
    document.documentElement.style.fontSize = sizes[fontSize] || '16px';
  }, [fontSize]);

  const toggleHighContrast = () => setHighContrast(prev => !prev);
  const toggleElderlyMode = () => setElderlyMode(prev => !prev);
  
  const increaseFontSize = () => {
    setFontSize(prev => {
      if (prev === 'normal') return 'large';
      if (prev === 'large') return 'extra-large';
      return prev;
    });
  };
  
  const decreaseFontSize = () => {
    setFontSize(prev => {
      if (prev === 'extra-large') return 'large';
      if (prev === 'large') return 'normal';
      return prev;
    });
  };

  const value = {
    highContrast,
    elderlyMode,
    fontSize,
    toggleHighContrast,
    toggleElderlyMode,
    increaseFontSize,
    decreaseFontSize,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
}

export function useAccessibility() {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
}
