export interface Business {
  id: string;
  name: string;
  domain: string;
  business_id: string;
  is_admin: boolean;
  visible_metrics: {
    show_response_time: boolean;
    show_message_volume: boolean;
    show_success_rate: boolean;
    show_cost: boolean;
    show_ai_settings: boolean;
    show_prompt: boolean;
  };
}

export interface NewBusinessForm {
  name: string;
  domain: string;
  passcode: string;
  business_id: string;
}
