import React, { createContext, useContext, useState, ReactNode } from 'react';

interface BusinessContextType {
  selectedBusinessId: string;
  setSelectedBusinessId: (id: string) => void;
  selectedBusinessName: string;
  setSelectedBusinessName: (name: string) => void;
}

const BusinessContext = createContext<BusinessContextType | undefined>(undefined);

export function BusinessProvider({ children }: { children: ReactNode }) {
  const [selectedBusinessId, setSelectedBusinessId] = useState('');
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
  if (context === undefined) {
    throw new Error('useBusiness must be used within a BusinessProvider');
  }
  return context;
}
