import React, { createContext, useContext, useState } from 'react';

interface Business {
  id: string;
  name: string;
  domain: string;
  business_id: string;
  is_admin: boolean;
  permissions: BusinessPermissions;
}

interface BusinessContextType {
  permissions: BusinessPermissions | null;
  setPermissions: (permissions: BusinessPermissions | null) => void;
  hasPermission: (permission: string) => boolean;
  canViewMetric: (metric: string) => boolean;
  isAdmin: boolean;
  business: Business | null;
  setBusiness: (business: Business | null) => void;
  logout: () => void;
}

interface BusinessPermissions {
  navigation: {
    workflows: boolean;
    analytics: boolean;
    settings: boolean;
    api_access: boolean;
  };
  analytics: {
    sms: {
      recent_conversations: boolean;
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

const BusinessContext = createContext<BusinessContextType | undefined>(undefined);

export function BusinessProvider({ children }: { children: React.ReactNode }) {
  const [permissions, setPermissions] = useState<BusinessPermissions | null>(null);
  const [business, setBusiness] = useState<Business | null>(null);

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

  const logout = () => {
    setBusiness(null);
    setPermissions(null);
  };

  return (
    <BusinessContext.Provider value={{
      permissions,
      setPermissions,
      hasPermission,
      canViewMetric,
      isAdmin,
      business,
      setBusiness,
      logout
    }}>
      {children}
    </BusinessContext.Provider>
  );
}

export function useBusiness() {
  const context = useContext(BusinessContext);
  if (context === undefined) {
    throw new Error('useBusiness must be used within a BusinessProvider');
  }
  return context;
}
