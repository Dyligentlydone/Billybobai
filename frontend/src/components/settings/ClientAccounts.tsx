import React, { useState, useEffect } from 'react';
import { PlusIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { useBusiness } from '../../contexts/BusinessContext';
import { BACKEND_URL } from '../../config';

interface ClientPasscode {
  business_id: string;
  passcode: string;
  permissions: {
    navigation: {
      workflows: boolean;
      analytics: boolean;
      settings: boolean;
      api_access: boolean;
      dashboard: boolean;
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

interface PermissionSection {
  title: string;
  key: string;
  items: {
    key: string;
    label: string;
  }[];
}

const PERMISSION_SECTIONS: PermissionSection[] = [
  {
    title: 'Navigation Access',
    key: 'navigation',
    items: [
      { key: 'dashboard', label: 'Dashboard' },
      { key: 'workflows', label: 'Workflows' },
      { key: 'analytics', label: 'Analytics' },
      { key: 'settings', label: 'Settings' },
      { key: 'api_access', label: 'API Access' }
    ]
  },
  {
    title: 'SMS Analytics',
    key: 'analytics.sms',
    items: [
      { key: 'recent_conversations', label: 'Recent Conversations' },
      { key: 'response_time', label: 'Response Time' },
      { key: 'message_volume', label: 'Message Volume' },
      { key: 'success_rate', label: 'Success Rate' },
      { key: 'cost_per_message', label: 'Cost per Message' },
      { key: 'ai_usage', label: 'AI Usage Statistics' }
    ]
  },
  {
    title: 'Voice Analytics',
    key: 'analytics.voice',
    items: [
      { key: 'call_duration', label: 'Call Duration' },
      { key: 'call_volume', label: 'Call Volume' },
      { key: 'success_rate', label: 'Success Rate' },
      { key: 'cost_per_call', label: 'Cost per Call' }
    ]
  },
  {
    title: 'Email Analytics',
    key: 'analytics.email',
    items: [
      { key: 'delivery_rate', label: 'Delivery Rate' },
      { key: 'open_rate', label: 'Open Rate' },
      { key: 'response_rate', label: 'Response Rate' },
      { key: 'cost_per_email', label: 'Cost per Email' }
    ]
  }
];

const defaultClientState: ClientPasscode = {
  business_id: '',
  passcode: '',
  permissions: {
    navigation: {
      dashboard: true,
      workflows: false,
      analytics: true,
      settings: false,
      api_access: false,
    },
    analytics: {
      sms: {
        recent_conversations: true,
        response_time: true,
        message_volume: true,
        success_rate: true,
        cost_per_message: false,
        ai_usage: false
      },
      voice: {
        call_duration: true,
        call_volume: true,
        success_rate: true,
        cost_per_call: false
      },
      email: {
        delivery_rate: true,
        open_rate: true,
        response_rate: true,
        cost_per_email: false
      }
    }
  }
};

export default function ClientAccounts() {
  const { isAdmin, business } = useBusiness();
  const [clients, setClients] = useState<ClientPasscode[]>([]);
  const [showNewClientForm, setShowNewClientForm] = useState(false);
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [newClient, setNewClient] = useState<ClientPasscode>(defaultClientState);
  const [error, setError] = useState<string>('');

  // Set admin token in localStorage
  useEffect(() => {
    if (isAdmin) {
      localStorage.setItem('admin_token', '97225');
    }
  }, [isAdmin]);

  // Redirect if not admin
  useEffect(() => {
    if (!isAdmin) {
      window.location.href = '/';
    }
  }, [isAdmin]);

  // Fetch clients on mount
  useEffect(() => {
    if (isAdmin) {
      fetchClients();
    }
  }, [isAdmin]);

  const fetchClients = async () => {
    try {
      const adminToken = localStorage.getItem('admin_token');
      // Always use the BACKEND_URL constant which already contains a safe
      // fallback to the production backend if the env var is missing.
      const baseUrl = BACKEND_URL;
      
      // Get the actual business ID from the business object
      const businessId = business?.business_id || business?.id || '';
      console.log("Using business ID for fetch:", businessId);
      
      // Use the direct-clients endpoint that's confirmed registered in the deployment
      const url = `${baseUrl}/api/auth/direct-clients?admin=${adminToken}&business_id=${businessId}`;
      console.log("Fetching clients from:", url);
      
      // Use fetch API for consistent behavior
      fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Clients data received:", data);
        setClients(data.clients || []);
      })
      .catch(error => {
        console.error("Error fetching clients:", error);
        setClients([]);
      });
    } catch (error) {
      console.error('Failed to fetch clients:', error);
    }
  };

  const toggleSection = (sectionKey: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionKey) 
        ? prev.filter(key => key !== sectionKey)
        : [...prev, sectionKey]
    );
  };

  // Helper function to get nested object value by path
  const getNestedValue = (obj: any, path: string) => {
    return path.split('.').reduce((acc, part) => acc?.[part], obj);
  };

  // Helper function to set nested object value by path
  const setNestedValue = (obj: any, path: string, value: any) => {
    const parts = path.split('.');
    const lastPart = parts.pop()!;
    const target = parts.reduce((acc, part) => {
      if (!acc[part]) acc[part] = {};
      return acc[part];
    }, obj);
    target[lastPart] = value;
    return obj;
  };

  // Helper function to flatten permissions object for API
  const flattenPermissions = (permissions: any) => {
    const result: { [key: string]: boolean } = {};
    
    // Process navigation permissions
    Object.entries(permissions.navigation).forEach(([key, value]) => {
      result[`navigation.${key}`] = Boolean(value);
    });
    
    // Process SMS analytics permissions
    Object.entries(permissions.analytics.sms).forEach(([key, value]) => {
      result[`analytics.sms.${key}`] = Boolean(value);
    });
    
    // Process voice analytics permissions
    Object.entries(permissions.analytics.voice).forEach(([key, value]) => {
      result[`analytics.voice.${key}`] = Boolean(value);
    });
    
    // Process email analytics permissions
    Object.entries(permissions.analytics.email).forEach(([key, value]) => {
      result[`analytics.email.${key}`] = Boolean(value);
    });
    
    return result;
  };

  const togglePermission = (section: string, key: string) => {
    console.log('Toggling permission:', section, key);
    setNewClient(prev => {
      const path = `${section}.${key}`;
      const currentValue = getNestedValue(prev.permissions, path);
      console.log('Current value:', currentValue);
      
      const newPermissions = JSON.parse(JSON.stringify(prev.permissions));
      setNestedValue(newPermissions, path, !currentValue);
      
      console.log('New permissions:', newPermissions);
      return {
        ...prev,
        permissions: newPermissions
      };
    });
  };

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Additional validation for business ID
    if (!newClient.business_id || newClient.business_id.trim() === '') {
      setError('Business ID is required');
      return;
    }

    if (newClient.passcode.length !== 5 || !/^\d+$/.test(newClient.passcode)) {
      setError('Passcode must be exactly 5 digits');
      return;
    }

    try {
      const adminToken = localStorage.getItem('admin_token');
      
      // Create a better structured permissions object for the backend
      const flatPermissions = flattenPermissions(newClient.permissions);
      
      // Always use the business_id the user typed in the form, NOT the one
      // from the BusinessContext (that may be "admin").
      const businessId = newClient.business_id.trim();
      console.log('Creating client for business_id:', businessId);
      
      // Prepare data for API call.  Backend expects admin_token optionally in
      // the body as well, so include it for completeness.
      const clientData = {
        business_id: businessId,
        passcode: newClient.passcode,
        permissions: flatPermissions,
        admin_token: adminToken,
      };
      
      console.log("Sending client data:", JSON.stringify(clientData));
      
      // Always use the BACKEND_URL constant to avoid environment-variable or
      // CORS misconfig that leads to 404s.
      const baseUrl = BACKEND_URL;
      
      // Use the direct-client-create endpoint for client creation.  Admin
      // token is now in the body so we don't need to duplicate it in the
      // query string, but keep it for backward compatibility.
      const url = `${baseUrl}/api/auth/direct-client-create?admin=${adminToken}`;
      
      // Use fetch API instead of XMLHttpRequest for better error handling
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(clientData),
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data && !data.error) {
          setShowNewClientForm(false);
          setNewClient(defaultClientState);
          fetchClients();
        } else {
          const errorMessage = data.message || data.error || 'Failed to create client access';
          console.error("API error response:", errorMessage);
          setError(errorMessage);
        }
      })
      .catch(error => {
        console.error('Network error occurred:', error);
        setError('Failed to create client access: Network error');
      });
    } catch (error) {
      console.error('Failed to create client:', error);
      setError('Failed to create client access: Network error');
    }
  };

  if (!isAdmin) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Client Access</h2>
        <button
          onClick={() => setShowNewClientForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Client Access
        </button>
      </div>

      {/* New Client Form */}
      {showNewClientForm && (
        <div className="bg-white shadow sm:rounded-lg p-6">
          <h3 className="text-lg font-medium mb-4">Add Client Access</h3>
          <form onSubmit={handleCreateClient} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Business ID</label>
                <input
                  type="text"
                  value={newClient.business_id}
                  onChange={(e) => setNewClient({ ...newClient, business_id: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
                <p className="mt-1 text-sm text-gray-500">
                  This ID should match their Twilio business identifier
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Passcode (5 digits)</label>
                <input
                  type="text"
                  value={newClient.passcode}
                  onChange={(e) => setNewClient({ ...newClient, passcode: e.target.value })}
                  pattern="[0-9]{5}"
                  maxLength={5}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Dashboard Permissions</h4>
              {PERMISSION_SECTIONS.map((section) => (
                <div key={section.key} className="border rounded-lg overflow-hidden">
                  <button
                    type="button"
                    onClick={() => toggleSection(section.key)}
                    className="w-full flex justify-between items-center px-4 py-3 bg-gray-50 hover:bg-gray-100"
                  >
                    <span className="font-medium text-gray-900">{section.title}</span>
                    {expandedSections.includes(section.key) ? (
                      <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                    ) : (
                      <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                    )}
                  </button>
                  
                  {expandedSections.includes(section.key) && (
                    <div className="p-4 space-y-3 bg-white">
                      {section.items.map((item) => (
                        <label key={item.key} className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={getNestedValue(newClient.permissions, `${section.key}.${item.key}`)}
                            onChange={() => togglePermission(section.key, item.key)}
                            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                          />
                          <span className="text-sm text-gray-700">{item.label}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowNewClientForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Client List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {clients.map((client) => (
            <li key={client.business_id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Business ID: {client.business_id}</h3>
                  <p className="text-sm text-gray-500">Passcode: {client.passcode}</p>
                  <div className="mt-2">
                    <h4 className="text-sm font-medium text-gray-700">Navigation Access:</h4>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {Object.entries(client.permissions.navigation)
                        .filter(([_, enabled]) => enabled)
                        .map(([key]) => (
                          <span 
                            key={key}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                          >
                            {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                          </span>
                        ))}
                    </div>
                    
                    <h4 className="text-sm font-medium text-gray-700 mt-2">Analytics Access:</h4>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {['sms', 'voice', 'email'].map(channel => (
                        Object.entries(client.permissions.analytics[channel as keyof typeof client.permissions.analytics])
                          .filter(([_, enabled]) => enabled)
                          .map(([key]) => (
                            <span 
                              key={`${channel}-${key}`}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
                            >
                              {`${channel.toUpperCase()}: ${key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}`}
                            </span>
                          ))
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
