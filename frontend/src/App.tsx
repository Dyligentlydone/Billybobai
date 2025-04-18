import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { SnackbarProvider } from './contexts/SnackbarContext';
import { BusinessProvider } from './contexts/BusinessContext';
import Dashboard from './pages/Dashboard';
import Workflows from './pages/Workflows';
import Clients from './pages/Clients';
import Settings from './pages/Settings';
import Analytics from './pages/Analytics';
import VoiceSetup from './pages/VoiceSetup';
import Layout from './components/Layout';
import PasscodePage from './pages/PasscodePage';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <SnackbarProvider>
      <BusinessProvider>
        <Router>
          <Routes>
            <Route path="/passcode" element={<PasscodePage />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/workflows" element={<Workflows />} />
                    <Route path="/voice-setup" element={<VoiceSetup />} />
                    <Route path="/clients" element={<Clients />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/analytics" element={<Analytics />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            } />
          </Routes>
          <Toaster position="top-right" />
        </Router>
      </BusinessProvider>
    </SnackbarProvider>
  );
}

export default App;
