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
}

const defaultContext: BusinessContextType = {
  selectedBusinessId: null,
  setSelectedBusinessId: () => {},
  permissions: null,
  setPermissions: () => {},
  hasPermission: () => false,
  canViewMetric: () => false,
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

  const hasPermission = (permission: string): boolean => {
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
    return hasPermission(`analytics.${metric}`);
  };

  return (
    <BusinessContext.Provider value={{
      selectedBusinessId,
      setSelectedBusinessId,
      permissions,
      setPermissions,
      hasPermission,
      canViewMetric
    }}>
      {children}
    </BusinessContext.Provider>
  );
}
