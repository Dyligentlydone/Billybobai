import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Dashboard from './pages/Dashboard';
import Workflows from './pages/Workflows';
import Clients from './pages/Clients';
import Settings from './pages/Settings';
import Analytics from './pages/Analytics';
import VoiceSetup from './pages/VoiceSetup';
import Layout from './components/Layout';

function App() {
  return (
    <>
      <Router>
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
      </Router>
      <Toaster position="top-right" />
    </>
  );
}

export default App;
