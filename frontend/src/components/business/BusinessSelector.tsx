import { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useBusiness } from '../../contexts/BusinessContext';

interface Business {
  id: string;
  name: string;
  active: boolean;
}

export default function BusinessSelector() {
  const [manualBusinessId, setManualBusinessId] = useState('');
  const { selectedBusinessId, setSelectedBusinessId } = useBusiness();

  // Fetch list of businesses
  const { data: businesses, isError } = useQuery<Business[]>(
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

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualBusinessId.trim()) {
      setSelectedBusinessId(manualBusinessId.trim());
      setManualBusinessId('');
    }
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value === 'manual') return; // Don't do anything if they select the manual option

    const business = businesses?.find(b => b.id === value);
    if (business) {
      setSelectedBusinessId(business.id);
    }
  };

  return (
    <div className="flex items-center space-x-4">
      <select
        value={selectedBusinessId || ''}
        onChange={handleSelectChange}
        className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
      >
        <option value="">Select a business</option>
        {businesses?.map((business) => (
          <option key={business.id} value={business.id}>
            {business.name || business.id}
          </option>
        ))}
        <option value="manual">Enter manually...</option>
      </select>

      {/* Manual business ID input */}
      <form onSubmit={handleManualSubmit} className="flex-1">
        <div className="mt-1 flex rounded-md shadow-sm">
          <input
            type="text"
            value={manualBusinessId}
            onChange={(e) => setManualBusinessId(e.target.value)}
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
