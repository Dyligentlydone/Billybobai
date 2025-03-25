import { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

interface EmailConfigWizardProps {
  onComplete: (config: any) => void;
  onCancel: () => void;
}

interface EmailTemplate {
  id: string;
  name: string;
  description: string;
  subject: string;
  content: string;
  style: 'SUPPORT' | 'MARKETING' | 'TRANSACTIONAL';
  variables: string[];
  customization?: {
    tone?: string;
    customVariables?: { [key: string]: string };
    schedule?: {
      frequency?: 'immediate' | 'scheduled' | 'triggered';
      trigger?: string;
      delay?: string;
    };
    abTesting?: {
      enabled?: boolean;
      variants?: {
        subject?: string[];
        content?: string[];
      };
    };
  };
}

interface EmailConfig {
  business: {
    name: string;
    domain: string;
    subdomain?: string;
    supportEmail: string;
    timezone: string;
    industry: string;
    size: 'small' | 'medium' | 'large' | 'enterprise';
  };
  integration: {
    sendgrid: {
      apiKey: string;
      domain: string;
      fromEmail: string;
      fromName: string;
      inboundDomain?: string;
      inboundSubdomain?: string;
      mxRecords?: {
        host: string;
        priority: number;
        value: string;
      }[];
    };
    openai: {
      apiKey: string;
      model: string;
      maxTokens?: number;
    };
  };
  brandTone: {
    voiceType: string;
    greetings: string[];
    wordsToAvoid: string[];
  };
  templates: {
    businessHours: {
      enabled: boolean;
      timezone: string;
      hours: {
        [key: string]: {
          start: string;
          end: string;
        };
      };
    };
    outOfOffice: string;
    selectedTemplates: {
      support: { [key: string]: EmailTemplate };
      marketing: { [key: string]: EmailTemplate };
      transactional: { [key: string]: EmailTemplate };
    };
  };
}

const DEFAULT_TEMPLATES: { [key: string]: EmailTemplate[] } = {
  support: [
    {
      id: 'support_inquiry',
      name: 'Support Inquiry Response',
      description: 'AI-powered response to customer support inquiries',
      subject: 'Re: {{subject}}',
      content: '',
      style: 'SUPPORT',
      variables: ['customer_name', 'inquiry_summary', 'case_number']
    },
    {
      id: 'support_followup',
      name: 'Support Follow-up',
      description: 'Check on customer satisfaction after support interaction',
      subject: 'Following up on your recent support request',
      content: '',
      style: 'SUPPORT',
      variables: ['customer_name', 'case_number', 'previous_interaction']
    }
  ],
  marketing: [
    {
      id: 'welcome_series_1',
      name: 'Welcome Email #1',
      description: 'First email in welcome series for new users',
      subject: 'Welcome to {{company_name}}!',
      content: '',
      style: 'MARKETING',
      variables: ['user_name', 'company_name', 'getting_started_steps']
    },
    {
      id: 'product_announcement',
      name: 'Product Announcement',
      description: 'Announce new features or products',
      subject: 'New: {{feature_name}} is here!',
      content: '',
      style: 'MARKETING',
      variables: ['user_name', 'feature_name', 'feature_benefits', 'cta_link']
    },
    {
      id: 'special_offer',
      name: 'Special Offer',
      description: 'Promotional email with special offers',
      subject: 'Special offer just for you!',
      content: '',
      style: 'MARKETING',
      variables: ['user_name', 'offer_details', 'discount_code', 'expiry_date']
    }
  ],
  transactional: [
    {
      id: 'order_confirmation',
      name: 'Order Confirmation',
      description: 'Confirm order details after purchase',
      subject: 'Order Confirmation #{{order_number}}',
      content: '',
      style: 'TRANSACTIONAL',
      variables: ['customer_name', 'order_number', 'order_details', 'shipping_info']
    },
    {
      id: 'appointment_reminder',
      name: 'Appointment Reminder',
      description: 'Remind customers of upcoming appointments',
      subject: 'Reminder: Your appointment on {{date}}',
      content: '',
      style: 'TRANSACTIONAL',
      variables: ['customer_name', 'appointment_date', 'appointment_time', 'location']
    },
    {
      id: 'password_reset',
      name: 'Password Reset',
      description: 'Send password reset instructions',
      subject: 'Password Reset Request',
      content: '',
      style: 'TRANSACTIONAL',
      variables: ['user_name', 'reset_link', 'expiry_time']
    }
  ]
};

export default function EmailConfigWizard({
  onComplete,
  onCancel,
}: EmailConfigWizardProps) {
  const [step, setStep] = useState(1);
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<EmailConfig>();
  const [selectedTemplates, setSelectedTemplates] = useState<{[key: string]: {[id: string]: boolean}}>({
    support: {},
    marketing: {},
    transactional: {}
  });
  const [expandedTemplate, setExpandedTemplate] = useState<string | null>(null);
  const [previewContent, setPreviewContent] = useState<string>('');

  const handleTemplateSelection = (category: string, templateId: string, checked: boolean) => {
    setSelectedTemplates(prev => {
      const updated = {
        ...prev,
        [category]: {
          ...prev[category],
          [templateId]: checked
        }
      };
      
      // Convert selected template IDs to template objects
      const selectedTemplateObjects = {
        support: Object.fromEntries(
          DEFAULT_TEMPLATES.support
            .filter(t => updated.support[t.id])
            .map(t => [t.id, t])
        ),
        marketing: Object.fromEntries(
          DEFAULT_TEMPLATES.marketing
            .filter(t => updated.marketing[t.id])
            .map(t => [t.id, t])
        ),
        transactional: Object.fromEntries(
          DEFAULT_TEMPLATES.transactional
            .filter(t => updated.transactional[t.id])
            .map(t => [t.id, t])
        )
      };
      
      setValue('templates.selectedTemplates', selectedTemplateObjects);
      return updated;
    });
  };

  const updateTemplateField = (template: EmailTemplate, field: string, value: any) => {
    setValue(`templates.selectedTemplates.${template.style.toLowerCase()}.${template.id}.${field}` as any, value);
  };

  const handleTemplateExpand = async (template: EmailTemplate) => {
    if (expandedTemplate === template.id) {
      setExpandedTemplate(null);
    } else {
      setExpandedTemplate(template.id);
      // Generate AI preview based on template and brand voice
      try {
        setPreviewContent('Generating preview...');
        // TODO: Call AI service to generate preview
        setPreviewContent('Sample email content based on template and brand voice...');
      } catch (error) {
        console.error('Failed to generate preview:', error);
        setPreviewContent('Failed to generate preview');
      }
    }
  };

  const onSubmit = async (data: EmailConfig) => {
    try {
      // Save API keys to environment
      const config = {
        business: {
          name: data.business.name,
          domain: data.business.domain,
          subdomain: data.business.subdomain,
          supportEmail: data.business.supportEmail,
          timezone: data.business.timezone,
          industry: data.business.industry,
          size: data.business.size,
        },
        integration: {
          sendgrid: {
            apiKey: data.integration.sendgrid.apiKey,
            domain: data.integration.sendgrid.domain,
            fromEmail: data.integration.sendgrid.fromEmail,
            fromName: data.integration.sendgrid.fromName,
            inboundDomain: data.integration.sendgrid.inboundDomain,
            inboundSubdomain: data.integration.sendgrid.inboundSubdomain,
            mxRecords: data.integration.sendgrid.mxRecords,
          },
          openai: {
            apiKey: data.integration.openai.apiKey,
            model: data.integration.openai.model,
            maxTokens: data.integration.openai.maxTokens,
          }
        },
        brandTone: data.brandTone,
        templates: data.templates
      };

      // Call parent's onComplete with config
      onComplete(config);
    } catch (error) {
      toast.error('Failed to save configuration');
      console.error('Config error:', error);
    }
  };

  return (
    <div className="space-y-8 divide-y divide-gray-200">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Business Configuration
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure your business settings.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-3">
                <label htmlFor="businessName" className="block text-sm font-medium text-gray-700">
                  Business Name
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('business.name', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.business?.name && (
                    <p className="mt-2 text-sm text-red-600">Business name is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="businessDomain" className="block text-sm font-medium text-gray-700">
                  Business Domain
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('business.domain', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.business?.domain && (
                    <p className="mt-2 text-sm text-red-600">Business domain is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="businessSubdomain" className="block text-sm font-medium text-gray-700">
                  Business Subdomain
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('business.subdomain')}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="supportEmail" className="block text-sm font-medium text-gray-700">
                  Support Email
                </label>
                <div className="mt-1">
                  <input
                    type="email"
                    {...register('business.supportEmail', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.business?.supportEmail && (
                    <p className="mt-2 text-sm text-red-600">Support email is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="timezone" className="block text-sm font-medium text-gray-700">
                  Timezone
                </label>
                <div className="mt-1">
                  <select
                    {...register('business.timezone', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                  </select>
                  {errors.business?.timezone && (
                    <p className="mt-2 text-sm text-red-600">Timezone is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="industry" className="block text-sm font-medium text-gray-700">
                  Industry
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('business.industry', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.business?.industry && (
                    <p className="mt-2 text-sm text-red-600">Industry is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="size" className="block text-sm font-medium text-gray-700">
                  Company Size
                </label>
                <div className="mt-1">
                  <select
                    {...register('business.size', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="small">Small</option>
                    <option value="medium">Medium</option>
                    <option value="large">Large</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                  {errors.business?.size && (
                    <p className="mt-2 text-sm text-red-600">Company size is required</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                API Configuration
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure your API settings.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-4">
                <label htmlFor="sendgridApiKey" className="block text-sm font-medium text-gray-700">
                  SendGrid API Key
                </label>
                <div className="mt-1">
                  <input
                    type="password"
                    {...register('integration.sendgrid.apiKey', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.sendgrid?.apiKey && (
                    <p className="mt-2 text-sm text-red-600">API key is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-4">
                <label htmlFor="sendgridDomain" className="block text-sm font-medium text-gray-700">
                  SendGrid Domain
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('integration.sendgrid.domain', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.sendgrid?.domain && (
                    <p className="mt-2 text-sm text-red-600">Domain is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="sendgridFromEmail" className="block text-sm font-medium text-gray-700">
                  SendGrid From Email
                </label>
                <div className="mt-1">
                  <input
                    type="email"
                    {...register('integration.sendgrid.fromEmail', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.sendgrid?.fromEmail && (
                    <p className="mt-2 text-sm text-red-600">From email is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="sendgridFromName" className="block text-sm font-medium text-gray-700">
                  SendGrid From Name
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('integration.sendgrid.fromName', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.sendgrid?.fromName && (
                    <p className="mt-2 text-sm text-red-600">From name is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-4">
                <label htmlFor="openaiApiKey" className="block text-sm font-medium text-gray-700">
                  OpenAI API Key
                </label>
                <div className="mt-1">
                  <input
                    type="password"
                    {...register('integration.openai.apiKey', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.openai?.apiKey && (
                    <p className="mt-2 text-sm text-red-600">API key is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="openaiModel" className="block text-sm font-medium text-gray-700">
                  OpenAI Model
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('integration.openai.model', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.openai?.model && (
                    <p className="mt-2 text-sm text-red-600">Model is required</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Brand Voice Configuration
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Define how your automated emails should sound.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-3">
                <label htmlFor="voiceType" className="block text-sm font-medium text-gray-700">
                  Voice Type
                </label>
                <div className="mt-1">
                  <select
                    {...register('brandTone.voiceType', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="formal">Formal</option>
                  </select>
                </div>
              </div>

              <div className="sm:col-span-6">
                <label htmlFor="greetings" className="block text-sm font-medium text-gray-700">
                  Greetings (comma-separated)
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('brandTone.greetings')}
                    placeholder="Hi, Hello, Good morning"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
              </div>

              <div className="sm:col-span-6">
                <label htmlFor="wordsToAvoid" className="block text-sm font-medium text-gray-700">
                  Words to Avoid (comma-separated)
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('brandTone.wordsToAvoid')}
                    placeholder="yeah, nah, cool"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Email Templates
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure and customize your email templates. Each template can be enhanced with AI-powered content generation.
              </p>
            </div>

            <div className="space-y-8">
              {/* Support Templates */}
              <div>
                <h4 className="text-base font-medium text-gray-900">Support Templates</h4>
                <div className="mt-4 space-y-6">
                  {DEFAULT_TEMPLATES.support.map((template) => (
                    <div key={template.id} className="bg-white shadow sm:rounded-lg">
                      <div className="px-4 py-5 sm:p-6">
                        <div className="flex items-start">
                          <div className="flex h-5 items-center">
                            <input
                              type="checkbox"
                              checked={selectedTemplates.support[template.id]}
                              onChange={(e) => handleTemplateSelection('support', template.id, e.target.checked)}
                              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                          </div>
                          <div className="ml-3 flex-grow">
                            <div className="flex items-center justify-between">
                              <div>
                                <h3 className="text-lg font-medium leading-6 text-gray-900">{template.name}</h3>
                                <p className="mt-1 text-sm text-gray-500">{template.description}</p>
                              </div>
                              <button
                                type="button"
                                onClick={() => handleTemplateExpand(template)}
                                className="ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium leading-4 text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                              >
                                {expandedTemplate === template.id ? 'Close' : 'Customize'}
                              </button>
                            </div>

                            {expandedTemplate === template.id && (
                              <div className="mt-6 space-y-6 border-t border-gray-200 pt-6">
                                {/* Template Preview */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Preview</h4>
                                  <div className="mt-2 rounded-md bg-gray-50 p-4">
                                    <p className="text-sm text-gray-700">Subject: {template.subject}</p>
                                    <div className="mt-2 whitespace-pre-wrap text-sm text-gray-700">
                                      {previewContent}
                                    </div>
                                  </div>
                                </div>

                                {/* Tone Customization */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Tone Adjustment</h4>
                                  <div className="mt-2">
                                    <select
                                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      onChange={(e) => {
                                        updateTemplateField(template, 'customization.tone', e.target.value);
                                      }}
                                    >
                                      <option value="default">Use Brand Voice</option>
                                      <option value="formal">More Formal</option>
                                      <option value="casual">More Casual</option>
                                      <option value="friendly">More Friendly</option>
                                      <option value="professional">More Professional</option>
                                    </select>
                                  </div>
                                </div>

                                {/* Variable Customization */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Custom Variables</h4>
                                  <div className="mt-2 space-y-4">
                                    {template.variables.map((variable) => (
                                      <div key={variable} className="flex items-center space-x-4">
                                        <label className="w-1/3 text-sm font-medium text-gray-700">
                                          {variable}:
                                        </label>
                                        <input
                                          type="text"
                                          placeholder={`Default ${variable}`}
                                          className="block w-2/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                          onChange={(e) => {
                                            updateTemplateField(
                                              template,
                                              `customization.customVariables.${variable}`,
                                              e.target.value
                                            );
                                          }}
                                        />
                                      </div>
                                    ))}
                                  </div>
                                </div>

                                {/* A/B Testing */}
                                <div>
                                  <div className="flex items-center space-x-2">
                                    <input
                                      type="checkbox"
                                      className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.abTesting.enabled',
                                          e.target.checked
                                        );
                                      }}
                                    />
                                    <h4 className="text-sm font-medium text-gray-900">Enable A/B Testing</h4>
                                  </div>
                                  <div className="mt-4 space-y-4">
                                    <div>
                                      <label className="block text-sm font-medium text-gray-700">
                                        Alternative Subject Lines
                                      </label>
                                      <div className="mt-1">
                                        <textarea
                                          rows={2}
                                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                          placeholder="Enter alternative subject lines (one per line)"
                                          onChange={(e) => {
                                            updateTemplateField(
                                              template,
                                              'customization.abTesting.variants.subject',
                                              e.target.value.split('\n')
                                            );
                                          }}
                                        />
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                {/* Scheduling Options */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Scheduling</h4>
                                  <div className="mt-2">
                                    <select
                                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.schedule.frequency',
                                          e.target.value
                                        );
                                      }}
                                    >
                                      <option value="immediate">Send Immediately</option>
                                      <option value="scheduled">Schedule for Later</option>
                                      <option value="triggered">Event Triggered</option>
                                    </select>
                                  </div>
                                  <div className="mt-4">
                                    <label className="block text-sm font-medium text-gray-700">
                                      Delay/Trigger
                                    </label>
                                    <input
                                      type="text"
                                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      placeholder="e.g., 2h, 1d, or event name"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.schedule.delay',
                                          e.target.value
                                        );
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Marketing Templates - Similar structure */}
              <div>
                <h4 className="text-base font-medium text-gray-900">Marketing Templates</h4>
                <div className="mt-4 space-y-6">
                  {DEFAULT_TEMPLATES.marketing.map((template) => (
                    <div key={template.id} className="bg-white shadow sm:rounded-lg">
                      <div className="px-4 py-5 sm:p-6">
                        <div className="flex items-start">
                          <div className="flex h-5 items-center">
                            <input
                              type="checkbox"
                              checked={selectedTemplates.marketing[template.id]}
                              onChange={(e) => handleTemplateSelection('marketing', template.id, e.target.checked)}
                              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                          </div>
                          <div className="ml-3 flex-grow">
                            <div className="flex items-center justify-between">
                              <div>
                                <h3 className="text-lg font-medium leading-6 text-gray-900">{template.name}</h3>
                                <p className="mt-1 text-sm text-gray-500">{template.description}</p>
                              </div>
                              <button
                                type="button"
                                onClick={() => handleTemplateExpand(template)}
                                className="ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium leading-4 text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                              >
                                {expandedTemplate === template.id ? 'Close' : 'Customize'}
                              </button>
                            </div>

                            {expandedTemplate === template.id && (
                              <div className="mt-6 space-y-6 border-t border-gray-200 pt-6">
                                {/* Template Preview */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Preview</h4>
                                  <div className="mt-2 rounded-md bg-gray-50 p-4">
                                    <p className="text-sm text-gray-700">Subject: {template.subject}</p>
                                    <div className="mt-2 whitespace-pre-wrap text-sm text-gray-700">
                                      {previewContent}
                                    </div>
                                  </div>
                                </div>

                                {/* Tone Customization */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Tone Adjustment</h4>
                                  <div className="mt-2">
                                    <select
                                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      onChange={(e) => {
                                        updateTemplateField(template, 'customization.tone', e.target.value);
                                      }}
                                    >
                                      <option value="default">Use Brand Voice</option>
                                      <option value="formal">More Formal</option>
                                      <option value="casual">More Casual</option>
                                      <option value="friendly">More Friendly</option>
                                      <option value="professional">More Professional</option>
                                    </select>
                                  </div>
                                </div>

                                {/* Variable Customization */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Custom Variables</h4>
                                  <div className="mt-2 space-y-4">
                                    {template.variables.map((variable) => (
                                      <div key={variable} className="flex items-center space-x-4">
                                        <label className="w-1/3 text-sm font-medium text-gray-700">
                                          {variable}:
                                        </label>
                                        <input
                                          type="text"
                                          placeholder={`Default ${variable}`}
                                          className="block w-2/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                          onChange={(e) => {
                                            updateTemplateField(
                                              template,
                                              `customization.customVariables.${variable}`,
                                              e.target.value
                                            );
                                          }}
                                        />
                                      </div>
                                    ))}
                                  </div>
                                </div>

                                {/* A/B Testing */}
                                <div>
                                  <div className="flex items-center space-x-2">
                                    <input
                                      type="checkbox"
                                      className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.abTesting.enabled',
                                          e.target.checked
                                        );
                                      }}
                                    />
                                    <h4 className="text-sm font-medium text-gray-900">Enable A/B Testing</h4>
                                  </div>
                                  <div className="mt-4 space-y-4">
                                    <div>
                                      <label className="block text-sm font-medium text-gray-700">
                                        Alternative Subject Lines
                                      </label>
                                      <div className="mt-1">
                                        <textarea
                                          rows={2}
                                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                          placeholder="Enter alternative subject lines (one per line)"
                                          onChange={(e) => {
                                            updateTemplateField(
                                              template,
                                              'customization.abTesting.variants.subject',
                                              e.target.value.split('\n')
                                            );
                                          }}
                                        />
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                {/* Scheduling Options */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Scheduling</h4>
                                  <div className="mt-2">
                                    <select
                                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.schedule.frequency',
                                          e.target.value
                                        );
                                      }}
                                    >
                                      <option value="immediate">Send Immediately</option>
                                      <option value="scheduled">Schedule for Later</option>
                                      <option value="triggered">Event Triggered</option>
                                    </select>
                                  </div>
                                  <div className="mt-4">
                                    <label className="block text-sm font-medium text-gray-700">
                                      Delay/Trigger
                                    </label>
                                    <input
                                      type="text"
                                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      placeholder="e.g., 2h, 1d, or event name"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.schedule.delay',
                                          e.target.value
                                        );
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Transactional Templates - Similar structure */}
              <div>
                <h4 className="text-base font-medium text-gray-900">Transactional Templates</h4>
                <div className="mt-4 space-y-6">
                  {DEFAULT_TEMPLATES.transactional.map((template) => (
                    <div key={template.id} className="bg-white shadow sm:rounded-lg">
                      <div className="px-4 py-5 sm:p-6">
                        <div className="flex items-start">
                          <div className="flex h-5 items-center">
                            <input
                              type="checkbox"
                              checked={selectedTemplates.transactional[template.id]}
                              onChange={(e) => handleTemplateSelection('transactional', template.id, e.target.checked)}
                              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                          </div>
                          <div className="ml-3 flex-grow">
                            <div className="flex items-center justify-between">
                              <div>
                                <h3 className="text-lg font-medium leading-6 text-gray-900">{template.name}</h3>
                                <p className="mt-1 text-sm text-gray-500">{template.description}</p>
                              </div>
                              <button
                                type="button"
                                onClick={() => handleTemplateExpand(template)}
                                className="ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium leading-4 text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                              >
                                {expandedTemplate === template.id ? 'Close' : 'Customize'}
                              </button>
                            </div>

                            {expandedTemplate === template.id && (
                              <div className="mt-6 space-y-6 border-t border-gray-200 pt-6">
                                {/* Template Preview */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Preview</h4>
                                  <div className="mt-2 rounded-md bg-gray-50 p-4">
                                    <p className="text-sm text-gray-700">Subject: {template.subject}</p>
                                    <div className="mt-2 whitespace-pre-wrap text-sm text-gray-700">
                                      {previewContent}
                                    </div>
                                  </div>
                                </div>

                                {/* Tone Customization */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Tone Adjustment</h4>
                                  <div className="mt-2">
                                    <select
                                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      onChange={(e) => {
                                        updateTemplateField(template, 'customization.tone', e.target.value);
                                      }}
                                    >
                                      <option value="default">Use Brand Voice</option>
                                      <option value="formal">More Formal</option>
                                      <option value="casual">More Casual</option>
                                      <option value="friendly">More Friendly</option>
                                      <option value="professional">More Professional</option>
                                    </select>
                                  </div>
                                </div>

                                {/* Variable Customization */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Custom Variables</h4>
                                  <div className="mt-2 space-y-4">
                                    {template.variables.map((variable) => (
                                      <div key={variable} className="flex items-center space-x-4">
                                        <label className="w-1/3 text-sm font-medium text-gray-700">
                                          {variable}:
                                        </label>
                                        <input
                                          type="text"
                                          placeholder={`Default ${variable}`}
                                          className="block w-2/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                          onChange={(e) => {
                                            updateTemplateField(
                                              template,
                                              `customization.customVariables.${variable}`,
                                              e.target.value
                                            );
                                          }}
                                        />
                                      </div>
                                    ))}
                                  </div>
                                </div>

                                {/* A/B Testing */}
                                <div>
                                  <div className="flex items-center space-x-2">
                                    <input
                                      type="checkbox"
                                      className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.abTesting.enabled',
                                          e.target.checked
                                        );
                                      }}
                                    />
                                    <h4 className="text-sm font-medium text-gray-900">Enable A/B Testing</h4>
                                  </div>
                                  <div className="mt-4 space-y-4">
                                    <div>
                                      <label className="block text-sm font-medium text-gray-700">
                                        Alternative Subject Lines
                                      </label>
                                      <div className="mt-1">
                                        <textarea
                                          rows={2}
                                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                          placeholder="Enter alternative subject lines (one per line)"
                                          onChange={(e) => {
                                            updateTemplateField(
                                              template,
                                              'customization.abTesting.variants.subject',
                                              e.target.value.split('\n')
                                            );
                                          }}
                                        />
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                {/* Scheduling Options */}
                                <div>
                                  <h4 className="text-sm font-medium text-gray-900">Scheduling</h4>
                                  <div className="mt-2">
                                    <select
                                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.schedule.frequency',
                                          e.target.value
                                        );
                                      }}
                                    >
                                      <option value="immediate">Send Immediately</option>
                                      <option value="scheduled">Schedule for Later</option>
                                      <option value="triggered">Event Triggered</option>
                                    </select>
                                  </div>
                                  <div className="mt-4">
                                    <label className="block text-sm font-medium text-gray-700">
                                      Delay/Trigger
                                    </label>
                                    <input
                                      type="text"
                                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                      placeholder="e.g., 2h, 1d, or event name"
                                      onChange={(e) => {
                                        updateTemplateField(
                                          template,
                                          'customization.schedule.delay',
                                          e.target.value
                                        );
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 5 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Business Hours & Settings
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure when and how to respond to emails.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    {...register('templates.businessHours.enabled')}
                    className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <label htmlFor="businessHoursEnabled" className="ml-2 block text-sm text-gray-700">
                    Enable Business Hours
                  </label>
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="timezone" className="block text-sm font-medium text-gray-700">
                  Timezone
                </label>
                <div className="mt-1">
                  <select
                    {...register('templates.businessHours.timezone')}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                  </select>
                </div>
              </div>

              <div className="sm:col-span-6">
                <label htmlFor="outOfOffice" className="block text-sm font-medium text-gray-700">
                  Out of Office Message
                </label>
                <div className="mt-1">
                  <textarea
                    {...register('templates.outOfOffice')}
                    rows={3}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    placeholder="Thank you for your email. Our office is currently closed..."
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="pt-5">
          <div className="flex justify-end space-x-3">
            {step > 1 && (
              <button
                type="button"
                onClick={() => setStep(step - 1)}
                className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Previous
              </button>
            )}
            <button
              type="button"
              onClick={onCancel}
              className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Cancel
            </button>
            {step < 5 ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Create
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
