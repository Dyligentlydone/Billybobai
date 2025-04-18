import React, { createContext, useContext, useState } from 'react';

interface BusinessPermissions {
  navigation: {
    workflows: boolean;
    analytics: boolean;
    settings: boolean;
    api_access: boolean;
  };
  analytics: {
    sms: {
      response_time: boolean;
      message_volume: boolean;
      success_rate: boolean;
      cost_per_message: boolean;
      ai_usage: boolean;
    };
    voice: {
      call_duration: boolean;
      call_volume: boolean;
      success_rate: boolean;
      cost_per_call: boolean;
    };
    email: {
      delivery_rate: boolean;
      open_rate: boolean;
      response_rate: boolean;
      cost_per_email: boolean;
    };
  };
}

interface Business {
  id: string;
  name: string;
  domain: string;
  business_id: string;
  is_admin: boolean;
  permissions?: BusinessPermissions;
  visible_metrics?: {
    [key: string]: boolean;
  };
}

interface BusinessContextType {
  business: Business | null;
  setBusiness: (business: Business | null) => void;
  isAdmin: boolean;
  hasPermission: (path: string) => boolean;
  canViewMetric: (metric: keyof Business['visible_metrics']) => boolean;
}

const defaultContext: BusinessContextType = {
  business: null,
  setBusiness: () => {},
  isAdmin: false,
  hasPermission: () => false,
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
    return business.visible_metrics?.[metric] ?? false;
  };

  // Compute isAdmin from business
  const isAdmin = business?.is_admin ?? false;

  // Helper function to check nested permissions
  const hasPermission = (path: string): boolean => {
    if (isAdmin) return true;
    if (!business?.permissions) return false;

    return path.split('.').reduce((acc: any, part) => acc?.[part], business.permissions) ?? false;
  };

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
        hasPermission,
        canViewMetric
      }}
    >
      {children}
    </BusinessContext.Provider>
  );
}
