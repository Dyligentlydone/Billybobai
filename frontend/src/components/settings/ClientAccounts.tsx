import React, { useState, useEffect } from 'react';
import { PlusIcon, PencilIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { Business, NewBusinessForm } from '../../types/business';
import { useBusiness } from '../../contexts/BusinessContext';

export default function ClientAccounts() {
  const { isAdmin } = useBusiness();
  const [clients, setClients] = useState<Business[]>([]);
  const [showNewClientForm, setShowNewClientForm] = useState(false);
  const [editingClient, setEditingClient] = useState<string | null>(null);
  const [newClient, setNewClient] = useState<NewBusinessForm>({
    name: '',
    domain: '',
    passcode: '',
    business_id: ''
  });

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
      const response = await fetch('/api/auth/businesses');
      if (response.ok) {
        const data = await response.json();
        setClients(data.businesses);
      }
    } catch (error) {
      console.error('Failed to fetch clients:', error);
    }
  };

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/auth/businesses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newClient)
      });

      if (response.ok) {
        setShowNewClientForm(false);
        setNewClient({ name: '', domain: '', passcode: '', business_id: '' });
        fetchClients();
      }
    } catch (error) {
      console.error('Failed to create client:', error);
    }
  };

  const handleUpdateMetrics = async (clientId: string, metrics: Record<string, boolean>) => {
    try {
      const response = await fetch(`/api/auth/businesses/${clientId}/metrics`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ visible_metrics: metrics })
      });

      if (response.ok) {
        fetchClients();
        setEditingClient(null);
      }
    } catch (error) {
      console.error('Failed to update metrics:', error);
    }
  };

  if (!isAdmin) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Client Accounts</h2>
        <button
          onClick={() => setShowNewClientForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Client
        </button>
      </div>

      {/* New Client Form */}
      {showNewClientForm && (
        <div className="bg-white shadow sm:rounded-lg p-6">
          <h3 className="text-lg font-medium mb-4">Add New Client</h3>
          <form onSubmit={handleCreateClient} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Business Name</label>
              <input
                type="text"
                value={newClient.name}
                onChange={(e) => setNewClient({ ...newClient, name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Domain</label>
              <input
                type="text"
                value={newClient.domain}
                onChange={(e) => setNewClient({ ...newClient, domain: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              />
            </div>
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
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              />
            </div>
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
            <li key={client.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{client.name}</h3>
                  <p className="text-sm text-gray-500">{client.domain}</p>
                  <p className="text-xs text-gray-400">Business ID: {client.business_id}</p>
                </div>
                <button
                  onClick={() => setEditingClient(editingClient === client.id ? null : client.id)}
                  className="inline-flex items-center px-3 py-1 border border-transparent rounded-md text-sm font-medium text-indigo-600 hover:text-indigo-700"
                >
                  <PencilIcon className="h-4 w-4 mr-1" />
                  Edit Access
                </button>
              </div>

              {/* Metrics Editor */}
              {editingClient === client.id && (
                <div className="mt-4 space-y-3">
                  <h4 className="text-sm font-medium text-gray-700">Visible Metrics</h4>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(client.visible_metrics).map(([key, value]) => (
                      <button
                        key={key}
                        onClick={() => handleUpdateMetrics(client.id, {
                          ...client.visible_metrics,
                          [key]: !value
                        })}
                        className={`flex items-center justify-between px-4 py-2 rounded-md ${
                          value ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-500'
                        }`}
                      >
                        <span className="text-sm">
                          {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </span>
                        {value ? (
                          <EyeIcon className="h-5 w-5" />
                        ) : (
                          <EyeSlashIcon className="h-5 w-5" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
