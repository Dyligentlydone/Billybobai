import React, { createContext, useContext, useState } from 'react';

interface BusinessContextType {
  selectedBusinessId: string | null;
  setSelectedBusinessId: (id: string | null) => void;
}

const defaultContext: BusinessContextType = {
  selectedBusinessId: null,
  setSelectedBusinessId: () => {}
};

const BusinessContext = createContext<BusinessContextType>(defaultContext);

export function useBusiness() {
  const context = useContext(BusinessContext);
  if (!context) {
    throw new Error('useBusiness must be used within a BusinessProvider');
  }
  return context;
}

export function BusinessProvider({ children }: { children: React.ReactNode }) {
  const [selectedBusinessId, setSelectedBusinessId] = useState<string | null>(null);

  return (
    <BusinessContext.Provider 
      value={{ 
        selectedBusinessId, 
        setSelectedBusinessId
      }}
    >
      {children}
    </BusinessContext.Provider>
  );
}
