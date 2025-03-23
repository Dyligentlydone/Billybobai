import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';

interface Business {
  id: string;
  name: string;
  active: boolean;
}

interface BusinessSelectorProps {
  onBusinessChange: (businessId: string) => void;
}

export default function BusinessSelector({ onBusinessChange }: BusinessSelectorProps) {
  const [selectedBusiness, setSelectedBusiness] = useState<string>('');

  const { data: businesses, isLoading } = useQuery(
    'businesses',
    async () => {
      const { data } = await axios.get('/api/businesses');
      return data as Business[];
    },
    {
      refetchInterval: 300000 // Refresh every 5 minutes
    }
  );

  useEffect(() => {
    if (businesses?.length > 0 && !selectedBusiness) {
      setSelectedBusiness(businesses[0].id);
      onBusinessChange(businesses[0].id);
    }
  }, [businesses, selectedBusiness, onBusinessChange]);

  if (isLoading) {
    return (
      <div className="animate-pulse h-10 w-48 bg-gray-200 rounded"></div>
    );
  }

  return (
    <div className="flex items-center space-x-4">
      <label htmlFor="business-select" className="text-sm font-medium text-gray-700">
        Select Business
      </label>
      <select
        id="business-select"
        value={selectedBusiness}
        onChange={(e) => {
          setSelectedBusiness(e.target.value);
          onBusinessChange(e.target.value);
        }}
        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
      >
        {businesses?.map((business) => (
          <option key={business.id} value={business.id}>
            {business.name} {!business.active && '(Inactive)'}
          </option>
        ))}
      </select>
    </div>
  );
}
