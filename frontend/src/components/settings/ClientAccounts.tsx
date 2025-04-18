import React, { useState, useEffect } from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';
import { useBusiness } from '../../contexts/BusinessContext';

interface ClientPasscode {
  business_id: string;
  passcode: string;
}

export default function ClientAccounts() {
  const { isAdmin } = useBusiness();
  const [clients, setClients] = useState<ClientPasscode[]>([]);
  const [showNewClientForm, setShowNewClientForm] = useState(false);
  const [newClient, setNewClient] = useState<ClientPasscode>({
    business_id: '',
    passcode: ''
  });
  const [error, setError] = useState<string>('');

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
      const response = await fetch('/api/auth/passcodes');
      if (response.ok) {
        const data = await response.json();
        setClients(data.clients);
      }
    } catch (error) {
      console.error('Failed to fetch clients:', error);
    }
  };

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newClient.passcode.length !== 5 || !/^\d+$/.test(newClient.passcode)) {
      setError('Passcode must be exactly 5 digits');
      return;
    }

    try {
      const response = await fetch('/api/auth/passcodes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newClient)
      });

      if (response.ok) {
        setShowNewClientForm(false);
        setNewClient({ business_id: '', passcode: '' });
        fetchClients();
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to create client access');
      }
    } catch (error) {
      console.error('Failed to create client:', error);
      setError('Failed to create client access');
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
          <form onSubmit={handleCreateClient} className="space-y-4">
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
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
