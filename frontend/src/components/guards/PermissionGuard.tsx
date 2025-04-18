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
  const { hasPermission } = useBusiness();

  if (!hasPermission(requiredPermission)) {
    return <Navigate to={fallbackPath} replace />;
  }

  return <>{children}</>;
}
