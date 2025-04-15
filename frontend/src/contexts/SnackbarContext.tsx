import React from 'react';
import { SnackbarProvider as MuiSnackbarProvider, enqueueSnackbar as notistackEnqueueSnackbar } from 'notistack';

// Re-export the enqueueSnackbar function
export const enqueueSnackbar = notistackEnqueueSnackbar;

// Create a provider component that wraps the MUI Snackbar provider
export const SnackbarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <MuiSnackbarProvider 
      maxSnack={3}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
    >
      {children}
    </MuiSnackbarProvider>
  );
};
