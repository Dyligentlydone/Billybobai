export interface EmailConfig {
  sendgrid: {
    type: 'email';
    aiEnabled: boolean;
    fromEmail: string;
    fromName: string;
    prompt: string;
  };
  instructions: string[];
}
