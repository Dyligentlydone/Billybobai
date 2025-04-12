export interface CalendlyConfig {
  enabled: boolean;
  access_token: string;
  user_uri: string;
  webhook_uri: string;
  default_event_type: string;
  booking_window_days: number;
  min_notice_hours: number;
  reminder_hours: number[];
  allow_cancellation: boolean;
  allow_rescheduling: boolean;
}

export const DEFAULT_CALENDLY_CONFIG: CalendlyConfig = {
  enabled: false,
  access_token: '',
  user_uri: '',
  webhook_uri: '',
  default_event_type: '',
  booking_window_days: 14,
  min_notice_hours: 4,
  reminder_hours: [24, 48],
  allow_cancellation: true,
  allow_rescheduling: true,
};

// Utility functions for Calendly operations
export const calendlyUtils = {
  validateConfig: (config: CalendlyConfig) => {
    if (!config.enabled) return true;
    return !!(
      config.access_token &&
      config.user_uri &&
      config.default_event_type
    );
  },
  
  formatEventDuration: (minutes: number) => {
    if (minutes < 60) return `${minutes} minutes`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes 
      ? `${hours}h ${remainingMinutes}m`
      : `${hours} hour${hours > 1 ? 's' : ''}`;
  }
};
