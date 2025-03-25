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
  integration: {
    sendgridApiKey: string;
    fromEmail: string;
    fromName: string;
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
      support: {
        [key: string]: EmailTemplate & {
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
        };
      };
      marketing: {
        [key: string]: EmailTemplate & {
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
        };
      };
      transactional: {
        [key: string]: EmailTemplate & {
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
        };
      };
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

  const onSubmit = (data: EmailConfig) => {
    if (!data.integration.sendgridApiKey || !data.integration.fromEmail || !data.integration.fromName) {
      toast.error('Please fill in all SendGrid integration details before creating');
      return;
    }
    
    onComplete({
      ...data,
      brandTone: {
        ...data.brandTone,
        greetings: data.brandTone.greetings ? data.brandTone.greetings[0].split(',').map(g => g.trim()) : [],
        wordsToAvoid: data.brandTone.wordsToAvoid ? data.brandTone.wordsToAvoid[0].split(',').map(w => w.trim()) : []
      }
    });
  };

  return (
    <div className="space-y-8 divide-y divide-gray-200">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                SendGrid Integration
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure your SendGrid email settings.
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
                    {...register('integration.sendgridApiKey', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.sendgridApiKey && (
                    <p className="mt-2 text-sm text-red-600">API key is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="fromEmail" className="block text-sm font-medium text-gray-700">
                  From Email
                </label>
                <div className="mt-1">
                  <input
                    type="email"
                    {...register('integration.fromEmail', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.fromEmail && (
                    <p className="mt-2 text-sm text-red-600">From email is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="fromName" className="block text-sm font-medium text-gray-700">
                  From Name
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('integration.fromName', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.fromName && (
                    <p className="mt-2 text-sm text-red-600">From name is required</p>
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

        {step === 3 && (
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

        {step === 4 && (
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
            {step < 4 ? (
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
