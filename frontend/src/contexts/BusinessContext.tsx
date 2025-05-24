import React, { createContext, useContext, useState, useEffect } from 'react';
import { BusinessPermissions, DEFAULT_PERMISSIONS } from '../utils/permissions';

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
  // New properties for client passcode business locking
  lockedBusinessId: string | null;
  setLockedBusinessId: (id: string | null) => void;
  isBusinessLocked: boolean;
}

const defaultContext: BusinessContextType = {
  selectedBusinessId: null,
  setSelectedBusinessId: () => {},
  permissions: DEFAULT_PERMISSIONS,
  setPermissions: () => {},
  hasPermission: () => false,
  canViewMetric: () => false,
  isAdmin: false,
  business: null,
  setBusiness: () => {},
  logout: () => {},
  // New properties for client passcode business locking
  lockedBusinessId: null,
  setLockedBusinessId: () => {},
  isBusinessLocked: false
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
  // New state for client passcode business locking
  const [lockedBusinessId, setLockedBusinessId] = useState<string | null>(() => {
    const stored = localStorage.getItem('lockedBusinessId');
    return stored || null;
  });
  
  // If business is locked, force selectedBusinessId to match lockedBusinessId
  useEffect(() => {
    if (lockedBusinessId && selectedBusinessId !== lockedBusinessId) {
      setSelectedBusinessId(lockedBusinessId);
    }
  }, [lockedBusinessId, selectedBusinessId]);

  // Clear authentication on mount if no valid business data
  useEffect(() => {
    const storedBusiness = localStorage.getItem('business');
    if (!storedBusiness) {
      localStorage.removeItem('isAuthenticated');
    }
  }, []);

  const isAdmin = business?.is_admin ?? false;

  const hasPermission = (permission: string): boolean => {
    console.log('hasPermission called for:', permission);
    
    // Admin users have access to everything
    if (isAdmin) {
      console.log('Admin access granted automatically');
      return true;
    }
    
    // Check if permissions object exists
    if (!permissions) {
      console.log('No permissions object found, denying access');
      return false;
    }
    
    // Split the permission path (e.g., 'navigation.dashboard' -> ['navigation', 'dashboard'])
    const parts = permission.split('.');
    console.log('Permission parts:', parts);
    
    let current: any = { ...permissions };
    
    // Special case handling for common permissions
    if (permission === 'navigation.dashboard' && current?.navigation?.dashboard === true) {
      console.log('Dashboard access granted via navigation.dashboard permission');
      return true;
    }
    
    if (permission === 'navigation.analytics' && current?.navigation?.analytics === true) {
      console.log('Analytics access granted via navigation.analytics permission');
      return true;
    }
    
    // Regular permission path traversal
    try {
      for (const part of parts) {
        if (current[part] === undefined) {
          console.log(`Permission denied: part "${part}" not found in current permissions object`, current);
          return false;
        }
        current = current[part];
      }
      
      const result = Boolean(current);
      console.log('Permission check result:', result);
      return result;
    } catch (error) {
      console.error('Error checking permission:', error);
      return false;
    }
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
    setLockedBusinessId(null);
    localStorage.removeItem('business');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('lockedBusinessId');
  };

  // Calculate if business is locked (client passcode login)
  const isBusinessLocked = Boolean(lockedBusinessId);

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
      logout,
      lockedBusinessId,
      setLockedBusinessId,
      isBusinessLocked
    }}>
      {children}
    </BusinessContext.Provider>
  );
}
