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
  const { selectedBusinessId, setSelectedBusinessId, setSelectedBusinessName } = useBusiness();

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
      setSelectedBusinessName(`Business ${manualBusinessId.trim()}`);
      setManualBusinessId('');
    }
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value === 'manual') return; // Don't do anything if they select the manual option

    const business = businesses?.find(b => b.id === value);
    if (business) {
      setSelectedBusinessId(business.id);
      setSelectedBusinessName(business.name);
    }
  };

  return (
    <div className="flex gap-2 items-start">
      {/* Dropdown for existing businesses */}
      <select
        value={selectedBusinessId || 'manual'}
        onChange={handleSelectChange}
        className="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
      >
        <option value="manual">Select Business ID...</option>
        {(businesses || [])?.map((business) => (
          <option key={business.id} value={business.id}>
            {business.name} (ID: {business.id})
          </option>
        ))}
      </select>

      {/* Manual input form */}
      <form onSubmit={handleManualSubmit} className="flex gap-2">
        <input
          type="text"
          value={manualBusinessId}
          onChange={(e) => setManualBusinessId(e.target.value)}
          placeholder="Or enter Business ID"
          className="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        />
        <button
          type="submit"
          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Set
        </button>
      </form>
    </div>
  );
}
