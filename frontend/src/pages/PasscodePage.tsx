import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useBusiness } from '../contexts/BusinessContext';
import axios from 'axios';

interface Business {
  id: string;
  name: string;
  domain: string;
  business_id: string;
  is_admin: boolean;
  permissions: {
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
  };
}

export default function PasscodePage() {
  const [passcode, setPasscode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { setBusiness, setPermissions } = useBusiness();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Admin passcode check
    const adminPasscode = '97225';
    if (passcode === adminPasscode) {
      const adminBusiness: Business = {
        id: 'admin',
        name: 'Admin',
        domain: 'admin',
        business_id: 'admin',
        is_admin: true,
        permissions: {
          navigation: {
            workflows: true,
            analytics: true,
            settings: true,
            api_access: true,
          },
          analytics: {
            sms: {
              recent_conversations: true,
              response_time: true,
              message_volume: true,
              success_rate: true,
              cost_per_message: true,
              ai_usage: true,
            },
            voice: {
              call_duration: true,
              call_volume: true,
              success_rate: true,
              cost_per_call: true,
            },
            email: {
              delivery_rate: true,
              open_rate: true,
              response_rate: true,
              cost_per_email: true,
            },
          },
        },
      };
      
      setBusiness(adminBusiness);
      setPermissions(adminBusiness.permissions);
      
      setTimeout(() => {
        navigate('/analytics');
      }, 800);
    } else {
      try {
        // First, find the business_id by passcode
        const passcodesResponse = await axios.post('/api/auth/passcodes', { passcode });
        const { clients } = await passcodesResponse.data;
        
        const clientPasscode = clients.find((c: any) => c.passcode === passcode);
        
        if (!clientPasscode) {
          setError('Invalid passcode');
          setIsLoading(false);
          return;
        }

        // Then get the full business data
        const businessResponse = await axios.get(`/api/auth/businesses/${clientPasscode.business_id}`);
        if (!businessResponse.data) {
          setError('Failed to load business data');
          setIsLoading(false);
          return;
        }

        const businessData = businessResponse.data;
        
        // Set business data with permissions
        setBusiness({
          ...businessData,
          is_admin: false,
          permissions: clientPasscode.permissions
        });
        setPermissions(clientPasscode.permissions);
        
        setTimeout(() => {
          if (clientPasscode.permissions.navigation.analytics) {
            navigate('/analytics');
          } else if (clientPasscode.permissions.navigation.workflows) {
            navigate('/workflows');
          } else if (clientPasscode.permissions.navigation.settings) {
            navigate('/settings');
          } else {
            // Fallback to first available permission
            const availableRoute = Object.entries(clientPasscode.permissions.navigation)
              .find(([_, hasAccess]) => hasAccess);
            
            if (availableRoute) {
              navigate(`/${availableRoute[0]}`);
            } else {
              setError('No accessible routes available');
            }
          }
        }, 800);
      } catch (error) {
        console.error('Login failed:', error);
        setError('Invalid passcode');
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Enter your passcode
          </h2>
        </div>
        <motion.form 
          className="mt-8 space-y-6" 
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="passcode" className="sr-only">
                Passcode
              </label>
              <input
                id="passcode"
                name="passcode"
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter your passcode"
                value={passcode}
                onChange={(e) => setPasscode(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </div>

          {error && (
            <motion.div 
              className="text-red-600 text-sm text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              {error}
            </motion.div>
          )}

          <div>
            <motion.button
              type="submit"
              disabled={isLoading}
              className={`group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white ${
                isLoading
                  ? 'bg-indigo-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
              whileHover={{ scale: isLoading ? 1 : 1.02 }}
              whileTap={{ scale: isLoading ? 1 : 0.98 }}
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </motion.button>
          </div>
        </motion.form>
      </div>
    </div>
  );
}
