import React from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useBusiness } from '../../contexts/BusinessContext';

interface Business {
  id: string;
  name: string;
}

export default function BusinessSelector() {
  const { selectedBusinessId, setSelectedBusinessId } = useBusiness();

  // Fetch list of businesses
  const { data: businesses = [] } = useQuery<Business[]>(
    'businesses',
    async () => {
      try {
        const { data } = await axios.get('/api/businesses');
        return data;
      } catch (error) {
        console.error('Failed to fetch businesses:', error);
        return []; // Return empty array on error
      }
    },
    {
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  const handleManualSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const manualBusinessId = form.manualBusinessId.value;
    if (manualBusinessId.trim()) {
      setSelectedBusinessId(manualBusinessId.trim());
      form.reset();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <label htmlFor="business-select" className="text-sm font-medium text-gray-700">
          Business:
        </label>
        <select
          id="business-select"
          value={selectedBusinessId || ''}
          onChange={(e) => setSelectedBusinessId(e.target.value || null)}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        >
          <option value="">Select a business</option>
          {businesses.map((business) => (
            <option key={business.id} value={business.id}>
              {business.name}
            </option>
          ))}
        </select>
      </div>

      <form onSubmit={handleManualSubmit} className="mt-4">
        <label htmlFor="manualBusinessId" className="block text-sm font-medium text-gray-700">
          Or enter business ID manually:
        </label>
        <div className="mt-1 flex rounded-md shadow-sm">
          <input
            type="text"
            name="manualBusinessId"
            id="manualBusinessId"
            placeholder="Enter business ID"
            className="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
          <button
            type="submit"
            className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Set
          </button>
        </div>
      </form>
    </div>
  );
}
