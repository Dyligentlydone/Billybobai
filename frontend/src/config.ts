// Backend URL configuration
// Use Vite's import.meta.env for build-time injection.  Fallback to production
// backend URL if the env var is missing (prevents 404s when variable is
// misconfigured during deploy).
export const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL ||
  'https://billybobai-production.up.railway.app';

// Other configuration constants can be added here
export const DEFAULT_RETRY_COUNT = 3;
export const DEFAULT_RESPONSE_TIMEOUT = 5000; // 5 seconds
