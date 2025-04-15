import React, { createContext, useContext, useState, ReactNode } from 'react';

interface BusinessContextType {
  selectedBusinessId: string | null;
  setSelectedBusinessId: (id: string | null) => void;
  selectedBusinessName: string;
  setSelectedBusinessName: (name: string) => void;
}

const defaultContext: BusinessContextType = {
  selectedBusinessId: null,
  setSelectedBusinessId: () => {},
  selectedBusinessName: '',
  setSelectedBusinessName: () => {}
};

const BusinessContext = createContext<BusinessContextType>(defaultContext);

export function BusinessProvider({ children }: { children: ReactNode }) {
  const [selectedBusinessId, setSelectedBusinessId] = useState<string | null>(null);
  const [selectedBusinessName, setSelectedBusinessName] = useState('');

  return (
    <BusinessContext.Provider 
      value={{ 
        selectedBusinessId, 
        setSelectedBusinessId,
        selectedBusinessName,
        setSelectedBusinessName
      }}
    >
      {children}
    </BusinessContext.Provider>
  );
}

export function useBusiness() {
  const context = useContext(BusinessContext);
  if (!context) {
    throw new Error('useBusiness must be used within a BusinessProvider');
  }
  return context;
}
