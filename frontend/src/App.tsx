import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { SnackbarProvider } from './contexts/SnackbarContext';
import { BusinessProvider, useBusiness } from './contexts/BusinessContext';
import Dashboard from './pages/Dashboard';
import Workflows from './pages/Workflows';
import Clients from './pages/Clients';
import Settings from './pages/Settings';
import Analytics from './pages/Analytics';
import VoiceSetup from './pages/VoiceSetup';
import Layout from './components/Layout';
import PasscodePage from './pages/PasscodePage';
import PermissionGuard from './components/guards/PermissionGuard';

function RequireAuth({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const { business, logout } = useBusiness();
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  
  useEffect(() => {
    // If authenticated but no business data, logout and redirect
    if (isAuthenticated && !business) {
      logout();
      navigate('/passcode', { replace: true });
    }
  }, [isAuthenticated, business, logout, navigate]);

  if (!isAuthenticated || !business) {
    return <Navigate to="/passcode" replace />;
  }

  return <>{children}</>;
}

function AuthRedirect() {
  const { business } = useBusiness();
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  
  if (isAuthenticated && business) {
    return <Navigate to="/analytics" replace />;
  }

  return <Navigate to="/passcode" replace />;
}

function App() {
  return (
    <BusinessProvider>
      <SnackbarProvider>
        <Router>
          <Routes>
            {/* Public route */}
            <Route path="/passcode" element={
              <PublicRoute>
                <PasscodePage />
              </PublicRoute>
            } />
            
            {/* Root redirect */}
            <Route index element={<AuthRedirect />} />

            {/* Protected routes */}
            <Route element={<RequireAuth><Layout /></RequireAuth>}>              
              <Route
                path="dashboard"
                element={
                  <PermissionGuard requiredPermission="navigation.dashboard">
                    <Dashboard />
                  </PermissionGuard>
                }
              />
              
              <Route
                path="workflows"
                element={
                  <PermissionGuard requiredPermission="navigation.workflows">
                    <Workflows />
                  </PermissionGuard>
                }
              />
              
              <Route
                path="voice-setup"
                element={
                  <PermissionGuard requiredPermission="navigation.voice_setup">
                    <VoiceSetup />
                  </PermissionGuard>
                }
              />
              
              <Route
                path="clients"
                element={
                  <PermissionGuard requiredPermission="navigation.clients">
                    <Clients />
                  </PermissionGuard>
                }
              />
              
              <Route
                path="settings"
                element={
                  <PermissionGuard requiredPermission="navigation.settings">
                    <Settings />
                  </PermissionGuard>
                }
              />
              
              <Route
                path="analytics"
                element={
                  <PermissionGuard requiredPermission="navigation.analytics">
                    <Analytics />
                  </PermissionGuard>
                }
              />
            </Route>

            {/* Catch all other routes and redirect to passcode if not authenticated */}
            <Route path="*" element={<AuthRedirect />} />
          </Routes>
          <Toaster position="top-right" />
        </Router>
      </SnackbarProvider>
    </BusinessProvider>
  );
}

// Prevent authenticated users from accessing public routes
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { business } = useBusiness();
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  
  if (isAuthenticated && business) {
    return <Navigate to="/analytics" replace />;
  }

  return <>{children}</>;
}

export default App;
