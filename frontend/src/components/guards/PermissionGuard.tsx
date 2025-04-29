import React from 'react';
import { Navigate } from 'react-router-dom';
import { useBusiness } from '../../contexts/BusinessContext';

interface PermissionGuardProps {
  children: React.ReactNode;
  requiredPermission: string;
  fallbackPath?: string;
}

export default function PermissionGuard({ 
  children, 
  requiredPermission,
  fallbackPath = '/'
}: PermissionGuardProps) {
  const { hasPermission, permissions, isAdmin } = useBusiness();

  console.log('PermissionGuard checking:', requiredPermission);
  console.log('Current permissions structure:', permissions);
  console.log('Is admin:', isAdmin);
  
  // Check if user has the required permission
  const hasAccess = hasPermission(requiredPermission);
  console.log('Has permission:', hasAccess);

  if (!hasAccess) {
    console.log('Access denied, redirecting to:', fallbackPath);
    return <Navigate to={fallbackPath} replace />;
  }

  console.log('Access granted for:', requiredPermission);
  return <>{children}</>;
}
