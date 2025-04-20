interface WebhookUrls {
  twilio: string;
  sendgrid: string;
  zendesk: string;
}

export const getWebhookUrls = (): WebhookUrls => {
  // Use only VITE_BACKEND_URL, no fallback or alternate env var
  const baseUrl = import.meta.env.VITE_BACKEND_URL;
  return {
    twilio: `${baseUrl}/webhooks/twilio`,
    sendgrid: `${baseUrl}/webhooks/sendgrid`,
    zendesk: `${baseUrl}/webhooks/zendesk`
  };
};
