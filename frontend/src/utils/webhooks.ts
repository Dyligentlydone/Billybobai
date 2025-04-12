interface WebhookUrls {
  twilio: string;
  sendgrid: string;
  zendesk: string;
}

export const getWebhookUrls = (): WebhookUrls => {
  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  return {
    twilio: `${baseUrl}/webhooks/twilio`,
    sendgrid: `${baseUrl}/webhooks/sendgrid`,
    zendesk: `${baseUrl}/webhooks/zendesk`
  };
};
