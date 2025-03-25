/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_SENDGRID_API_KEY: string
  readonly VITE_OPENAI_API_KEY: string
  readonly VITE_TWILIO_ACCOUNT_SID: string
  readonly VITE_TWILIO_AUTH_TOKEN: string
  readonly VITE_ZENDESK_SUBDOMAIN: string
  readonly VITE_ZENDESK_API_TOKEN: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
