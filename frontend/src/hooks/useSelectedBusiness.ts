import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

interface Business {
  id: string;
  name: string;
}

export function useSelectedBusiness() {
  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(null);
  const location = useLocation();

  useEffect(() => {
    // Get business ID from URL or localStorage
    const businessId = new URLSearchParams(location.search).get('businessId') || 
                      localStorage.getItem('selectedBusinessId');
    
    if (businessId) {
      // In a real app, you'd fetch business details from an API
      // For now, we'll just create a simple object
      setSelectedBusiness({
        id: businessId,
        name: 'Business ' + businessId
      });
    } else {
      setSelectedBusiness(null);
    }
  }, [location]);

  return { selectedBusiness };
}
