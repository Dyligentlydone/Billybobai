import React, { useState, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useBusiness } from '../contexts/BusinessContext';

interface ClientPasscode {
  business_id: string;
  passcode: string;
}

export default function PasscodePage() {
  const [passcode, setPasscode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setBusiness } = useBusiness();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Admin passcode check
    const adminPasscode = '97225';
    
    if (passcode === adminPasscode) {
      // Set admin business data
      const adminBusiness = {
        id: 'admin',
        name: 'Admin Account',
        domain: 'admin.dyligent.ai',
        business_id: 'admin',
        is_admin: true,
        visible_metrics: {
          show_response_time: true,
          show_message_volume: true,
          show_success_rate: true,
          show_cost: true,
          show_ai_settings: true,
          show_prompt: true
        }
      };
      
      setBusiness(adminBusiness);
      localStorage.setItem('isAuthenticated', 'true');
      
      setTimeout(() => {
        navigate('/');
      }, 800);
    } else {
      try {
        // First, find the business_id by passcode
        const passcodesResponse = await fetch('/api/auth/passcodes');
        const { clients } = await passcodesResponse.json();
        
        const clientPasscode = clients.find((c: ClientPasscode) => c.passcode === passcode);
        
        if (!clientPasscode) {
          setError('Invalid passcode');
          setIsLoading(false);
          return;
        }

        // Then get the full business data
        const businessResponse = await fetch(`/api/auth/businesses/${clientPasscode.business_id}`);
        if (!businessResponse.ok) {
          setError('Failed to load business data');
          setIsLoading(false);
          return;
        }

        const businessData = await businessResponse.json();
        
        // Set business data with client flag
        setBusiness({
          ...businessData,
          is_admin: false
        });

        localStorage.setItem('isAuthenticated', 'true');
        
        setTimeout(() => {
          navigate('/');
        }, 800);
      } catch (error) {
        console.error('Login error:', error);
        setError('Failed to verify passcode');
        setIsLoading(false);
      }
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-4"
    >
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <motion.h1 
            initial={{ y: -20 }}
            animate={{ y: 0 }}
            className="text-4xl font-bold text-gold-400 mb-2"
          >
            Diligence on <span className="text-gold-300">LOCK</span>
          </motion.h1>
          <motion.p 
            initial={{ y: -20 }}
            animate={{ y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-gold-300"
          >
            Enter passcode to continue
          </motion.p>
        </div>

        <motion.form 
          onSubmit={handleSubmit}
          className="space-y-4"
        >
          <div>
            <motion.input
              type="password"
              value={passcode}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPasscode(e.target.value)}
              className="w-full px-4 py-3 bg-transparent border-none
                text-gold-300 placeholder-gold-600/50 focus:outline-none focus:ring-0
                text-center text-2xl tracking-[1em] font-light"
              placeholder="• • • • •"
              maxLength={5}
              pattern="[0-9]{5}"
              inputMode="numeric"
              autoFocus
            />
            {error && (
              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-2 text-sm text-red-500"
              >
                {error}
              </motion.p>
            )}
          </div>

          <motion.button
            type="submit"
            disabled={isLoading || passcode.length !== 5}
            className={`w-full py-3 rounded-lg text-gray-900 font-medium
              ${isLoading ? 'bg-gold-400' : 'bg-gold-500 hover:bg-gold-400'} 
              transition-colors focus:outline-none focus:ring-2 focus:ring-gold-400 focus:ring-offset-2 
              focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <motion.div 
                className="flex items-center justify-center"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <circle 
                    className="opacity-25" 
                    cx="12" 
                    cy="12" 
                    r="10" 
                    stroke="currentColor" 
                    strokeWidth="4"
                  />
                  <path 
                    className="opacity-75" 
                    fill="currentColor" 
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              </motion.div>
            ) : 'Enter'}
          </motion.button>
        </motion.form>
      </motion.div>
    </motion.div>
  );
}
