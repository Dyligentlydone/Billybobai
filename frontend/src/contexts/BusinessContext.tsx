import React, { createContext, useContext, useState, useEffect } from 'react';

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
      recent_conversations: boolean;
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
  selectedBusinessId: string | null;
  setSelectedBusinessId: (id: string | null) => void;
  permissions: BusinessPermissions | null;
  setPermissions: (permissions: BusinessPermissions | null) => void;
  hasPermission: (permission: string) => boolean;
  canViewMetric: (metric: string) => boolean;
  isAdmin: boolean;
  business: Business | null;
  setBusiness: (business: Business | null) => void;
  logout: () => void;
}

const defaultContext: BusinessContextType = {
  selectedBusinessId: null,
  setSelectedBusinessId: () => {},
  permissions: null,
  setPermissions: () => {},
  hasPermission: () => false,
  canViewMetric: () => false,
  isAdmin: false,
  business: null,
  setBusiness: () => {},
  logout: () => {}
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
  const [selectedBusinessId, setSelectedBusinessId] = useState<string | null>(null);
  const [permissions, setPermissions] = useState<BusinessPermissions | null>(null);
  const [business, setBusiness] = useState<Business | null>(() => {
    const stored = localStorage.getItem('business');
    return stored ? JSON.parse(stored) : null;
  });

  // Clear authentication on mount if no valid business data
  useEffect(() => {
    const storedBusiness = localStorage.getItem('business');
    if (!storedBusiness) {
      localStorage.removeItem('isAuthenticated');
    }
  }, []);

  const isAdmin = business?.is_admin ?? false;

  const hasPermission = (permission: string): boolean => {
    if (isAdmin) return true;
    if (!permissions) return false;
    
    const parts = permission.split('.');
    let current: any = permissions;
    
    for (const part of parts) {
      if (current[part] === undefined) return false;
      current = current[part];
    }
    
    return Boolean(current);
  };

  const canViewMetric = (metric: string): boolean => {
    if (isAdmin) return true;
    return hasPermission(`analytics.${metric}`);
  };

  // Update localStorage when business changes
  const handleSetBusiness = (newBusiness: Business | null) => {
    setBusiness(newBusiness);
    if (newBusiness) {
      localStorage.setItem('business', JSON.stringify(newBusiness));
    } else {
      localStorage.removeItem('business');
      localStorage.removeItem('isAuthenticated');
    }
  };

  // Logout function
  const logout = () => {
    setBusiness(null);
    setPermissions(null);
    setSelectedBusinessId(null);
    localStorage.removeItem('business');
    localStorage.removeItem('isAuthenticated');
  };

  return (
    <BusinessContext.Provider value={{
      selectedBusinessId,
      setSelectedBusinessId,
      permissions,
      setPermissions,
      hasPermission,
      canViewMetric,
      isAdmin,
      business,
      setBusiness: handleSetBusiness,
      logout
    }}>
      {children}
    </BusinessContext.Provider>
  );
}
