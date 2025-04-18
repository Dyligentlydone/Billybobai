import React, { createContext, useContext, useState } from 'react';
import { Business } from '../types/business';

interface BusinessContextType {
  business: Business | null;
  setBusiness: (business: Business | null) => void;
  isAdmin: boolean;
  canViewMetric: (metric: keyof Business['visible_metrics']) => boolean;
}

const defaultContext: BusinessContextType = {
  business: null,
  setBusiness: () => {},
  isAdmin: false,
  canViewMetric: () => false
};

const BusinessContext = createContext<BusinessContextType>(defaultContext);

export function useBusiness() {
  const context = useContext(BusinessContext);
  if (!context) {
    throw new Error('useBusiness must be used within a BusinessProvider');
  }
  return context;
}

export function BusinessProvider({ children }: { children: React.ReactNode }) {
  const [business, setBusiness] = useState<Business | null>(() => {
    const stored = localStorage.getItem('business');
    return stored ? JSON.parse(stored) : null;
  });

  // Helper function to check if a metric is visible
  const canViewMetric = (metric: keyof Business['visible_metrics']): boolean => {
    if (!business) return false;
    if (business.is_admin) return true;
    return business.visible_metrics[metric];
  };

  // Compute isAdmin from business
  const isAdmin = business?.is_admin ?? false;

  // Update localStorage when business changes
  const handleSetBusiness = (newBusiness: Business | null) => {
    setBusiness(newBusiness);
    if (newBusiness) {
      localStorage.setItem('business', JSON.stringify(newBusiness));
    } else {
      localStorage.removeItem('business');
    }
  };

  return (
    <BusinessContext.Provider 
      value={{ 
        business,
        setBusiness: handleSetBusiness,
        isAdmin,
        canViewMetric
      }}
    >
      {children}
    </BusinessContext.Provider>
  );
}
