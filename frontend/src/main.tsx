import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from 'react-query'
import axios from 'axios'
import App from './App.tsx'
import './index.css'

// Global axios configuration to enforce HTTPS
axios.defaults.baseURL = window.location.protocol + '//api.dyligent.xyz'
// Interceptor to ensure all requests use HTTPS
axios.interceptors.request.use(config => {
  // If there's a full URL in the request, make sure it uses HTTPS
  if (config.url?.startsWith('http:')) {
    config.url = config.url.replace('http:', 'https:')
  }
  return config
})

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
