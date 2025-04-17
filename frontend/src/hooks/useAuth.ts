import { useState, useEffect } from 'react';

interface User {
  id: string;
  clientId: string;
  email: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // In a real app, you'd check the session/token
    // For now, we'll just check localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  return { user };
}
