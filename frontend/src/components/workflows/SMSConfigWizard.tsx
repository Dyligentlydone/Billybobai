import { useState } from 'react';

interface BrandToneConfig {
  voiceType: 'professional' | 'friendly' | 'casual' | 'formal';
  greetings: string[];
  phrasingExamples: string[];
  wordsToAvoid: string[];
}

interface AITrainingConfig {
  openAIKey: string;
  qaPairs: Array<{ question: string; answer: string }>;
  faqDocuments: Array<{ name: string; content: string }>;
  chatHistory: Array<{ customer: string; response: string }>;
}

interface ContextConfig {
  memoryWindow: number;
  contextualTriggers: Array<{ trigger: string; response: string }>;
  knowledgeBase: Array<{ category: string; content: string }>;
  intentExamples: Array<{ intent: string; examples: string[] }>;
}

interface CalendlyConfig {
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
  sms_notifications: {
    enabled: boolean;
    include_cancel_link: boolean;
    include_reschedule_link: boolean;
    confirmation_message: string;
    reminder_message: string;
    cancellation_message: string;
    reschedule_message: string;
  };
}

interface SystemIntegrationConfig {
  zendesk: {
    enabled: boolean;
    email: string;
    apiToken: string;
    subdomain: string;
    defaultPriority: string;
    createTickets: boolean;
    updateExisting: boolean;
  };
  calendly: CalendlyConfig;
  webhook: {
    enabled: boolean;
    url: string;
    method: 'POST' | 'PUT';
    headers: Record<string, string>;
    events: string[];
  };
}

interface ResponseConfig {
  templates: Array<{
    name: string;
    template: string;
    variables: string[];
    description: string;
  }>;
  fallbackMessage: string;
  messageStructure: Array<{
    id: string;
    name: string;
    enabled: boolean;
    defaultContent: string;
  }>;
  characterLimit: number;
}

interface MonitoringConfig {
  alertThresholds: {
    responseTime: number;  // milliseconds
    errorRate: number;    // percentage
    dailyVolume: number;  // messages per day
  };
  slackNotifications: {
    enabled: boolean;
    webhookUrl: string;
    channel: string;     // without #
    mentionUser?: string; // for critical alerts
  };
  metrics: {
    responseTime: boolean;
    errorRate: boolean;
    messageVolume: boolean;
    aiConfidence: boolean;
    customerSentiment: boolean;
  };
  retention: {
    logsRetentionDays: number;
    messageHistoryDays: number;
  };
}

interface TwilioConfig {
  accountSid: string;
  authToken: string;
  phoneNumber: string;
  messagingServiceSid?: string;
  webhookUrl: string;
  fallbackUrl?: string;
  statusCallback?: string;
  retryCount: number;
}

interface Config {
  twilio: TwilioConfig;
  brandTone: BrandToneConfig;
  aiTraining: AITrainingConfig;
  context: ContextConfig;
  response: ResponseConfig;
  monitoring: MonitoringConfig;
  systemIntegration: SystemIntegrationConfig;
}

interface Props {
  onComplete: (config: Config) => void;
  onCancel: () => void;
}

const INITIAL_CONFIG: Config = {
  twilio: {
    accountSid: '',
    authToken: '',
    phoneNumber: '',
    messagingServiceSid: '',
    webhookUrl: '',
    fallbackUrl: '',
    statusCallback: '',
    retryCount: 3
  },
  brandTone: {
    voiceType: 'professional',
    greetings: [],
    phrasingExamples: [],
    wordsToAvoid: []
  },
  aiTraining: {
    openAIKey: '',
    qaPairs: [],
    faqDocuments: [],
    chatHistory: []
  },
  context: {
    memoryWindow: 5,
    contextualTriggers: [],
    knowledgeBase: [],
    intentExamples: []
  },
  response: {
    templates: [],
    fallbackMessage: "I apologize, but I'm having trouble understanding your request. Could you please rephrase it?",
    messageStructure: [
      {
        id: 'greeting',
        name: 'Greeting',
        enabled: true,
        defaultContent: 'Hi there!'
      },
      {
        id: 'mainContent',
        name: 'Main Content',
        enabled: true,
        defaultContent: '{content}'
      },
      {
        id: 'nextSteps',
        name: 'Next Steps',
        enabled: true,
        defaultContent: 'Here are the next steps: {steps}'
      },
      {
        id: 'signOff',
        name: 'Sign Off',
        enabled: true,
        defaultContent: 'Best regards'
      }
    ],
    characterLimit: 160
  },
  monitoring: {
    alertThresholds: {
      responseTime: 5000,  // 5 seconds
      errorRate: 5,       // 5%
      dailyVolume: 1000   // 1,000 messages/day
    },
    slackNotifications: {
      enabled: false,
      webhookUrl: '',
      channel: '',
      mentionUser: ''
    },
    metrics: {
      responseTime: true,
      errorRate: true,
      messageVolume: true,
      aiConfidence: true,
      customerSentiment: true
    },
    retention: {
      logsRetentionDays: 30,
      messageHistoryDays: 90
    }
  },
  systemIntegration: {
    zendesk: {
      enabled: false,
      email: '',
      apiToken: '',
      subdomain: '',
      defaultPriority: 'normal',
      createTickets: true,
      updateExisting: true
    },
    calendly: {
      enabled: false,
      access_token: '',
      user_uri: '',
      webhook_uri: '',
      default_event_type: '',
      booking_window_days: 14,
      min_notice_hours: 4,
      reminder_hours: [24],
      allow_cancellation: true,
      allow_rescheduling: true,
      sms_notifications: {
        enabled: false,
        include_cancel_link: false,
        include_reschedule_link: false,
        confirmation_message: '',
        reminder_message: '',
        cancellation_message: '',
        reschedule_message: ''
      }
    },
    webhook: {
      enabled: false,
      url: '',
      method: 'POST',
      headers: {},
      events: []
    }
  }
};

export default function SMSConfigWizard({ onComplete, onCancel }: Props) {
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState<Config>(INITIAL_CONFIG);
  const [newGreeting, setNewGreeting] = useState('');
  const [newPhrase, setNewPhrase] = useState('');
  const [newWordToAvoid, setNewWordToAvoid] = useState('');
  
  // AI Training state
  const [newQuestion, setNewQuestion] = useState('');
  const [newAnswer, setNewAnswer] = useState('');
  const [newFAQName, setNewFAQName] = useState('');
  const [newFAQContent, setNewFAQContent] = useState('');
  const [newCustomerMessage, setNewCustomerMessage] = useState('');
  const [newResponse, setNewResponse] = useState('');

  // Context state
  const [newTrigger, setNewTrigger] = useState('');
  const [newTriggerResponse, setNewTriggerResponse] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newIntent, setNewIntent] = useState('');
  const [newExample, setNewExample] = useState('');

  // Response Templates state
  const [newTemplateName, setNewTemplateName] = useState('');
  const [newTemplate, setNewTemplate] = useState('');
  const [newVariables, setNewVariables] = useState('');
  const [newDescription, setNewDescription] = useState('');

  // Message Structure state
  const [newSectionName, setNewSectionName] = useState('');
  const [newSectionContent, setNewSectionContent] = useState('');

  const handleVoiceTypeChange = (type: BrandToneConfig['voiceType']) => {
    setConfig(prev => ({
      ...prev,
      brandTone: {
        ...prev.brandTone,
        voiceType: type
      }
    }));
  };

  const addGreeting = () => {
    if (newGreeting.trim()) {
      setConfig(prev => ({
        ...prev,
        brandTone: {
          ...prev.brandTone,
          greetings: [...prev.brandTone.greetings, newGreeting.trim()]
        }
      }));
      setNewGreeting('');
    }
  };

  const addPhrase = () => {
    if (newPhrase.trim()) {
      setConfig(prev => ({
        ...prev,
        brandTone: {
          ...prev.brandTone,
          phrasingExamples: [...prev.brandTone.phrasingExamples, newPhrase.trim()]
        }
      }));
      setNewPhrase('');
    }
  };

  const addWordToAvoid = () => {
    if (newWordToAvoid.trim()) {
      setConfig(prev => ({
        ...prev,
        brandTone: {
          ...prev.brandTone,
          wordsToAvoid: [...prev.brandTone.wordsToAvoid, newWordToAvoid.trim()]
        }
      }));
      setNewWordToAvoid('');
    }
  };

  const addQAPair = () => {
    if (newQuestion.trim() && newAnswer.trim()) {
      setConfig(prev => ({
        ...prev,
        aiTraining: {
          ...prev.aiTraining,
          qaPairs: [...prev.aiTraining.qaPairs, {
            question: newQuestion.trim(),
            answer: newAnswer.trim()
          }]
        }
      }));
      setNewQuestion('');
      setNewAnswer('');
    }
  };

  const addFAQDocument = () => {
    if (newFAQName.trim() && newFAQContent.trim()) {
      setConfig(prev => ({
        ...prev,
        aiTraining: {
          ...prev.aiTraining,
          faqDocuments: [...prev.aiTraining.faqDocuments, {
            name: newFAQName.trim(),
            content: newFAQContent.trim()
          }]
        }
      }));
      setNewFAQName('');
      setNewFAQContent('');
    }
  };

  const addChatExample = () => {
    if (newCustomerMessage.trim() && newResponse.trim()) {
      setConfig(prev => ({
        ...prev,
        aiTraining: {
          ...prev.aiTraining,
          chatHistory: [...prev.aiTraining.chatHistory, {
            customer: newCustomerMessage.trim(),
            response: newResponse.trim()
          }]
        }
      }));
      setNewCustomerMessage('');
      setNewResponse('');
    }
  };

  const removeItem = (array: string[], index: number, field: keyof BrandToneConfig) => {
    setConfig(prev => ({
      ...prev,
      brandTone: {
        ...prev.brandTone,
        [field]: array.filter((_, i) => i !== index)
      }
    }));
  };

  const removeQAPair = (index: number) => {
    setConfig(prev => ({
      ...prev,
      aiTraining: {
        ...prev.aiTraining,
        qaPairs: prev.aiTraining.qaPairs.filter((_, i) => i !== index)
      }
    }));
  };

  const removeFAQDocument = (index: number) => {
    setConfig(prev => ({
      ...prev,
      aiTraining: {
        ...prev.aiTraining,
        faqDocuments: prev.aiTraining.faqDocuments.filter((_, i) => i !== index)
      }
    }));
  };

  const removeChatExample = (index: number) => {
    setConfig(prev => ({
      ...prev,
      aiTraining: {
        ...prev.aiTraining,
        chatHistory: prev.aiTraining.chatHistory.filter((_, i) => i !== index)
      }
    }));
  };

  const addContextualTrigger = () => {
    if (newTrigger.trim() && newTriggerResponse.trim()) {
      setConfig(prev => ({
        ...prev,
        context: {
          ...prev.context,
          contextualTriggers: [...prev.context.contextualTriggers, {
            trigger: newTrigger.trim(),
            response: newTriggerResponse.trim()
          }]
        }
      }));
      setNewTrigger('');
      setNewTriggerResponse('');
    }
  };

  const addKnowledgeItem = () => {
    if (newCategory.trim() && newContent.trim()) {
      setConfig(prev => ({
        ...prev,
        context: {
          ...prev.context,
          knowledgeBase: [...prev.context.knowledgeBase, {
            category: newCategory.trim(),
            content: newContent.trim()
          }]
        }
      }));
      setNewCategory('');
      setNewContent('');
    }
  };

  const addIntentExample = () => {
    if (newIntent.trim() && newExample.trim()) {
      const existingIntent = config.context.intentExamples.find(i => i.intent === newIntent.trim());
      
      if (existingIntent) {
        setConfig(prev => ({
          ...prev,
          context: {
            ...prev.context,
            intentExamples: prev.context.intentExamples.map(i =>
              i.intent === newIntent.trim()
                ? { ...i, examples: [...i.examples, newExample.trim()] }
                : i
            )
          }
        }));
      } else {
        setConfig(prev => ({
          ...prev,
          context: {
            ...prev.context,
            intentExamples: [...prev.context.intentExamples, {
              intent: newIntent.trim(),
              examples: [newExample.trim()]
            }]
          }
        }));
      }
      setNewExample('');
    }
  };

  const removeContextualTrigger = (index: number) => {
    setConfig(prev => ({
      ...prev,
      context: {
        ...prev.context,
        contextualTriggers: prev.context.contextualTriggers.filter((_, i) => i !== index)
      }
    }));
  };

  const removeKnowledgeItem = (index: number) => {
    setConfig(prev => ({
      ...prev,
      context: {
        ...prev.context,
        knowledgeBase: prev.context.knowledgeBase.filter((_, i) => i !== index)
      }
    }));
  };

  const removeIntentExample = (intent: string, example: string) => {
    setConfig(prev => ({
      ...prev,
      context: {
        ...prev.context,
        intentExamples: prev.context.intentExamples.map(i =>
          i.intent === intent
            ? { ...i, examples: i.examples.filter(e => e !== example) }
            : i
        ).filter(i => i.examples.length > 0)
      }
    }));
  };

  const addTemplate = () => {
    if (newTemplateName.trim() && newTemplate.trim()) {
      const variables = newVariables.split(',')
        .map(v => v.trim())
        .filter(v => v.length > 0);

      setConfig(prev => ({
        ...prev,
        response: {
          ...prev.response,
          templates: [...prev.response.templates, {
            name: newTemplateName.trim(),
            template: newTemplate.trim(),
            variables,
            description: newDescription.trim()
          }]
        }
      }));
      setNewTemplateName('');
      setNewTemplate('');
      setNewVariables('');
      setNewDescription('');
    }
  };

  const removeTemplate = (index: number) => {
    setConfig(prev => ({
      ...prev,
      response: {
        ...prev.response,
        templates: prev.response.templates.filter((_, i) => i !== index)
      }
    }));
  };

  const addMessageSection = () => {
    if (newSectionName.trim()) {
      setConfig(prev => ({
        ...prev,
        response: {
          ...prev.response,
          messageStructure: [...prev.response.messageStructure, {
            id: newSectionName.toLowerCase().replace(/\s+/g, '_'),
            name: newSectionName.trim(),
            enabled: true,
            defaultContent: newSectionContent.trim() || '{content}'
          }]
        }
      }));
      setNewSectionName('');
      setNewSectionContent('');
    }
  };

  const removeMessageSection = (id: string) => {
    setConfig(prev => ({
      ...prev,
      response: {
        ...prev.response,
        messageStructure: prev.response.messageStructure.filter(section => section.id !== id)
      }
    }));
  };

  const updateMessageSection = (id: string, updates: Partial<ResponseConfig['messageStructure'][0]>) => {
    setConfig(prev => ({
      ...prev,
      response: {
        ...prev.response,
        messageStructure: prev.response.messageStructure.map(section =>
          section.id === id ? { ...section, ...updates } : section
        )
      }
    }));
  };

  const handleZendeskChange = (updates: Partial<SystemIntegrationConfig['zendesk']>) => {
    setConfig(prev => ({
      ...prev,
      systemIntegration: {
        ...prev.systemIntegration,
        zendesk: {
          ...prev.systemIntegration.zendesk,
          ...updates
        }
      }
    }));
  };

  const handleCalendlyChange = (updates: Partial<SystemIntegrationConfig['calendly']>) => {
    setConfig(prev => ({
      ...prev,
      systemIntegration: {
        ...prev.systemIntegration,
        calendly: {
          ...prev.systemIntegration.calendly,
          ...updates
        }
      }
    }));
  };

  const handleWebhookChange = (updates: Partial<SystemIntegrationConfig['webhook']>) => {
    setConfig(prev => ({
      ...prev,
      systemIntegration: {
        ...prev.systemIntegration,
        webhook: {
          ...prev.systemIntegration.webhook,
          ...updates
        }
      }
    }));
  };

  const handlePhoneNumberChange = (phoneNumber: string) => {
    const formattedNumber = phoneNumber.replace(/\D/g, '');
    
    if (formattedNumber.length === 10) {
      setConfig(prev => ({
        ...prev,
        twilio: {
          ...prev.twilio,
          phoneNumber: `+1${formattedNumber}`
        }
      }));
    }
  };

  const renderBrandToneStep = () => (
    <div className="space-y-8">
      <div>
        <label className="block text-sm font-medium text-gray-700">Voice Type</label>
        <div className="mt-2 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {(['professional', 'friendly', 'casual', 'formal'] as const).map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => handleVoiceTypeChange(type)}
              className={`
                relative px-4 py-3 border rounded-lg shadow-sm text-sm font-medium
                ${config.brandTone.voiceType === type
                  ? 'border-indigo-500 ring-2 ring-indigo-500 text-indigo-700 bg-indigo-50'
                  : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
                }
              `}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Greetings</label>
        <div className="mt-2 flex gap-2">
          <input
            type="text"
            value={newGreeting}
            onChange={(e) => setNewGreeting(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addGreeting()}
            placeholder="Add a greeting..."
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <button
            type="button"
            onClick={addGreeting}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Add
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {config.brandTone.greetings.map((greeting, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-indigo-100 text-indigo-800"
            >
              {greeting}
              <button
                type="button"
                onClick={() => removeItem(config.brandTone.greetings, index, 'greetings')}
                className="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full text-indigo-400 hover:bg-indigo-200 hover:text-indigo-500"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Phrasing Examples</label>
        <div className="mt-2 flex gap-2">
          <input
            type="text"
            value={newPhrase}
            onChange={(e) => setNewPhrase(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addPhrase()}
            placeholder="Add a phrasing example..."
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <button
            type="button"
            onClick={addPhrase}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Add
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {config.brandTone.phrasingExamples.map((phrase, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-green-100 text-green-800"
            >
              {phrase}
              <button
                type="button"
                onClick={() => removeItem(config.brandTone.phrasingExamples, index, 'phrasingExamples')}
                className="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full text-green-400 hover:bg-green-200 hover:text-green-500"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Words to Avoid</label>
        <div className="mt-2 flex gap-2">
          <input
            type="text"
            value={newWordToAvoid}
            onChange={(e) => setNewWordToAvoid(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addWordToAvoid()}
            placeholder="Add a word to avoid..."
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <button
            type="button"
            onClick={addWordToAvoid}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Add
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {config.brandTone.wordsToAvoid.map((word, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-red-100 text-red-800"
            >
              {word}
              <button
                type="button"
                onClick={() => removeItem(config.brandTone.wordsToAvoid, index, 'wordsToAvoid')}
                className="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full text-red-400 hover:bg-red-200 hover:text-red-500"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAITrainingStep = () => (
    <div className="space-y-8">
      <div>
        <label className="block text-sm font-medium text-gray-700">OpenAI API Key</label>
        <div className="mt-2">
          <input
            type="password"
            value={config.aiTraining.openAIKey}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              aiTraining: {
                ...prev.aiTraining,
                openAIKey: e.target.value
              }
            }))}
            placeholder="sk-..."
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Q&A Pairs</label>
        <div className="mt-2 space-y-3">
          <div className="flex gap-2">
            <div className="flex-1">
              <input
                type="text"
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                placeholder="Question..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
            <div className="flex-1">
              <input
                type="text"
                value={newAnswer}
                onChange={(e) => setNewAnswer(e.target.value)}
                placeholder="Answer..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
            <button
              type="button"
              onClick={addQAPair}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add
            </button>
          </div>
          <div className="space-y-2">
            {config.aiTraining.qaPairs.map((pair, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Q: {pair.question}</p>
                  <p className="text-sm text-gray-600">A: {pair.answer}</p>
                </div>
                <button
                  type="button"
                  onClick={() => removeQAPair(index)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">FAQ Documents</label>
        <div className="mt-2 space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={newFAQName}
              onChange={(e) => setNewFAQName(e.target.value)}
              placeholder="Document name..."
              className="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <textarea
              value={newFAQContent}
              onChange={(e) => setNewFAQContent(e.target.value)}
              placeholder="Document content..."
              rows={2}
              className="block flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <button
              type="button"
              onClick={addFAQDocument}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add
            </button>
          </div>
          <div className="space-y-2">
            {config.aiTraining.faqDocuments.map((doc, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                  <p className="text-sm text-gray-600 line-clamp-2">{doc.content}</p>
                </div>
                <button
                  type="button"
                  onClick={() => removeFAQDocument(index)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Chat Examples</label>
        <div className="mt-2 space-y-3">
          <div className="flex gap-2">
            <div className="flex-1">
              <input
                type="text"
                value={newCustomerMessage}
                onChange={(e) => setNewCustomerMessage(e.target.value)}
                placeholder="Customer message..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
            <div className="flex-1">
              <input
                type="text"
                value={newResponse}
                onChange={(e) => setNewResponse(e.target.value)}
                placeholder="Ideal response..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
            <button
              type="button"
              onClick={addChatExample}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add
            </button>
          </div>
          <div className="space-y-2">
            {config.aiTraining.chatHistory.map((chat, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Customer: {chat.customer}</p>
                  <p className="text-sm text-gray-600">Response: {chat.response}</p>
                </div>
                <button
                  type="button"
                  onClick={() => removeChatExample(index)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderContextStep = () => (
    <div className="space-y-8">
      <div>
        <label className="block text-sm font-medium text-gray-700">Conversation Memory</label>
        <div className="mt-2">
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="1"
              max="20"
              value={config.context.memoryWindow}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                context: {
                  ...prev.context,
                  memoryWindow: parseInt(e.target.value) || 5
                }
              }))}
              className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <span className="text-sm text-gray-500">messages to remember</span>
          </div>
          <p className="mt-1 text-sm text-gray-500">
            How many previous messages should the AI remember for context?
          </p>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Contextual Triggers</label>
        <div className="mt-2 space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={newTrigger}
              onChange={(e) => setNewTrigger(e.target.value)}
              placeholder="When customer says..."
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <input
              type="text"
              value={newTriggerResponse}
              onChange={(e) => setNewTriggerResponse(e.target.value)}
              placeholder="AI should consider..."
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <button
              type="button"
              onClick={addContextualTrigger}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add
            </button>
          </div>
          <div className="space-y-2">
            {config.context.contextualTriggers.map((trigger, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Trigger: {trigger.trigger}</p>
                  <p className="text-sm text-gray-600">Response: {trigger.response}</p>
                </div>
                <button
                  type="button"
                  onClick={() => removeContextualTrigger(index)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Knowledge Base</label>
        <div className="mt-2 space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              placeholder="Category..."
              className="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <textarea
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              placeholder="Knowledge content..."
              rows={2}
              className="block flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <button
              type="button"
              onClick={addKnowledgeItem}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add
            </button>
          </div>
          <div className="space-y-2">
            {config.context.knowledgeBase.map((item, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{item.category}</p>
                  <p className="text-sm text-gray-600 line-clamp-2">{item.content}</p>
                </div>
                <button
                  type="button"
                  onClick={() => removeKnowledgeItem(index)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Intent Examples</label>
        <div className="mt-2 space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={newIntent}
              onChange={(e) => setNewIntent(e.target.value)}
              placeholder="Intent name..."
              className="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <input
              type="text"
              value={newExample}
              onChange={(e) => setNewExample(e.target.value)}
              placeholder="Example phrase..."
              className="block flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <button
              type="button"
              onClick={addIntentExample}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add
            </button>
          </div>
          <div className="space-y-4">
            {config.context.intentExamples.map((intent) => (
              <div key={intent.intent} className="p-3 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900 mb-2">{intent.intent}</h4>
                <div className="flex flex-wrap gap-2">
                  {intent.examples.map((example) => (
                    <span
                      key={example}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-purple-100 text-purple-800"
                    >
                      {example}
                      <button
                        type="button"
                        onClick={() => removeIntentExample(intent.intent, example)}
                        className="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full text-purple-400 hover:bg-purple-200 hover:text-purple-500"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderResponseStep = () => (
    <div className="space-y-8">
      <div>
        <label className="block text-sm font-medium text-gray-700">Message Structure</label>
        <div className="mt-2">
          <p className="text-sm text-gray-500 mb-3">
            Define the sections of your AI responses and their default content
          </p>
          
          {/* Add new section */}
          <div className="mb-4 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <input
                type="text"
                value={newSectionName}
                onChange={(e) => setNewSectionName(e.target.value)}
                placeholder="Section name..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
              <button
                type="button"
                onClick={addMessageSection}
                className="inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Add Section
              </button>
            </div>
            <textarea
              value={newSectionContent}
              onChange={(e) => setNewSectionContent(e.target.value)}
              placeholder="Default content... Use {variables} for placeholders"
              rows={2}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>

          {/* Existing sections */}
          <div className="space-y-4">
            {config.response.messageStructure.map((section) => (
              <div key={section.id} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={section.enabled}
                        onChange={(e) => updateMessageSection(section.id, { enabled: e.target.checked })}
                        className="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      />
                      <input
                        type="text"
                        value={section.name}
                        onChange={(e) => updateMessageSection(section.id, { name: e.target.value })}
                        className="block flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeMessageSection(section.id)}
                    className="ml-2 text-gray-400 hover:text-gray-500"
                  >
                    ×
                  </button>
                </div>
                <textarea
                  value={section.defaultContent}
                  onChange={(e) => updateMessageSection(section.id, { defaultContent: e.target.value })}
                  rows={2}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="Default content for this section..."
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Character Limit</label>
        <div className="mt-2">
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="50"
              max="1600"
              value={config.response.characterLimit}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                response: {
                  ...prev.response,
                  characterLimit: parseInt(e.target.value) || 160
                }
              }))}
              className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <span className="text-sm text-gray-500">characters per message</span>
          </div>
          <p className="mt-1 text-sm text-gray-500">
            Maximum length for each SMS message. Standard SMS limit is 160 characters.
          </p>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Fallback Message</label>
        <div className="mt-2">
          <textarea
            value={config.response.fallbackMessage}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              response: {
                ...prev.response,
                fallbackMessage: e.target.value
              }
            }))}
            rows={2}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Message to send when AI cannot understand the request..."
          />
          <p className="mt-1 text-sm text-gray-500">
            This message will be sent when the AI is unable to generate a suitable response.
          </p>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Response Templates</label>
        <div className="mt-2 space-y-3">
          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-4">Create New Template</h4>
            
            {/* Template Name and Category */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div>
                <label className="block text-sm font-medium text-gray-600">Template Name</label>
                <input
                  type="text"
                  value={newTemplateName}
                  onChange={(e) => setNewTemplateName(e.target.value)}
                  placeholder="e.g., Order Status Update"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600">Variables</label>
                <input
                  type="text"
                  value={newVariables}
                  onChange={(e) => setNewVariables(e.target.value)}
                  placeholder="e.g., orderNumber, status, delivery"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
            </div>

            {/* Template Content */}
            <div className="mb-3">
              <label className="block text-sm font-medium text-gray-600">Template Content</label>
              <textarea
                value={newTemplate}
                onChange={(e) => setNewTemplate(e.target.value)}
                placeholder="Your order #{orderNumber} is {status}. Expected delivery: {delivery}"
                rows={3}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
              <p className="mt-1 text-xs text-gray-500">
                Use {'{variable}'} syntax for variables. Example: Hello {'{name}'}, your order is {'{status}'}
              </p>
            </div>

            {/* Template Description */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-600">When to Use</label>
              <textarea
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="e.g., Use this template when customers ask about their order status"
                rows={2}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            {/* Preview Section */}
            {newTemplate && (
              <div className="mb-4 p-3 bg-gray-50 rounded border border-gray-200">
                <label className="block text-sm font-medium text-gray-600 mb-2">Preview</label>
                <div className="text-sm text-gray-800">
                  {newTemplate.replace(/{(\w+)}/g, (_match, variable) =>
                    `<span class="text-purple-600">[${variable}]</span>`
                  )}
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {newVariables.split(',')
                    .map(v => v.trim())
                    .filter(v => v.length > 0)
                    .map((variable) => (
                      <span
                        key={variable}
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                      >
                        {variable}
                      </span>
                    ))}
                </div>
              </div>
            )}

            <button
              type="button"
              onClick={addTemplate}
              disabled={!newTemplateName.trim() || !newTemplate.trim()}
              className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Add Template
            </button>
          </div>

          {/* Template List */}
          <div className="space-y-3">
            {config.response.templates.length > 0 ? (
              config.response.templates.map((template, index) => (
                <div key={index} className="p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-sm font-medium text-gray-900">{template.name}</h4>
                    <button
                      type="button"
                      onClick={() => removeTemplate(index)}
                      className="text-gray-400 hover:text-gray-500"
                    >
                      ×
                    </button>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                  <div className="p-3 bg-gray-50 rounded text-sm font-mono">
                    {template.template}
                  </div>
                  {template.variables.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {template.variables.map((variable) => (
                        <span
                          key={variable}
                          className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                        >
                          {variable}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-4 text-sm text-gray-500">
                No templates added yet. Templates help maintain consistent responses for common scenarios.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderMonitoringStep = () => (
    <div className="space-y-8">
      {/* Alert Thresholds */}
      <div>
        <label className="block text-sm font-medium text-gray-700">Alert Thresholds</label>
        <div className="mt-4 grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-600">Response Time</label>
            <div className="mt-1 flex items-center gap-2">
              <input
                type="number"
                min="1000"
                max="30000"
                step="100"
                value={config.monitoring.alertThresholds.responseTime}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    alertThresholds: {
                      ...prev.monitoring.alertThresholds,
                      responseTime: parseInt(e.target.value) || 5000
                    }
                  }
                }))}
                className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
              <span className="text-sm text-gray-500">ms</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">Alert if response takes longer than this</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Error Rate</label>
            <div className="mt-1 flex items-center gap-2">
              <input
                type="number"
                min="1"
                max="100"
                value={config.monitoring.alertThresholds.errorRate}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    alertThresholds: {
                      ...prev.monitoring.alertThresholds,
                      errorRate: parseInt(e.target.value) || 5
                    }
                  }
                }))}
                className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
              <span className="text-sm text-gray-500">%</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">Alert if error rate exceeds this percentage</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Daily Volume</label>
            <div className="mt-1 flex items-center gap-2">
              <input
                type="number"
                min="100"
                max="100000"
                step="100"
                value={config.monitoring.alertThresholds.dailyVolume}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    alertThresholds: {
                      ...prev.monitoring.alertThresholds,
                      dailyVolume: parseInt(e.target.value) || 1000
                    }
                  }
                }))}
                className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
              <span className="text-sm text-gray-500">msgs/day</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Alert if daily messages exceed this limit
            </p>
          </div>
        </div>
      </div>

      {/* Slack Notifications */}
      <div>
        <label className="block text-sm font-medium text-gray-700">Slack Notifications</label>
        <div className="mt-4 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={config.monitoring.slackNotifications.enabled}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    slackNotifications: {
                      ...prev.monitoring.slackNotifications,
                      enabled: e.target.checked
                    }
                  }
                }))}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label className="ml-2 block text-sm text-gray-700">
                Enable Slack Alerts
              </label>
            </div>
          </div>

          {config.monitoring.slackNotifications.enabled && (
            <div className="ml-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600">Webhook URL</label>
                <input
                  type="url"
                  value={config.monitoring.slackNotifications.webhookUrl}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    monitoring: {
                      ...prev.monitoring,
                      slackNotifications: {
                        ...prev.monitoring.slackNotifications,
                        webhookUrl: e.target.value
                      }
                    }
                  }))}
                  placeholder="https://hooks.slack.com/services/..."
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                <div className="mt-1 flex items-center gap-2">
                  <a 
                    href="https://api.slack.com/messaging/webhooks" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-indigo-600 hover:text-indigo-500"
                  >
                    How to get webhook URL
                  </a>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600">Channel</label>
                <div className="mt-1 flex items-center">
                  <span className="text-gray-500 text-sm mr-2">#</span>
                  <input
                    type="text"
                    value={config.monitoring.slackNotifications.channel}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      monitoring: {
                        ...prev.monitoring,
                        slackNotifications: {
                          ...prev.monitoring.slackNotifications,
                          channel: e.target.value.replace(/^#/, '')
                        }
                      }
                    }))}
                    placeholder="alerts"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Channel name without the # symbol
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600">Critical Alert Mentions</label>
                <div className="mt-1 flex items-center">
                  <span className="text-gray-500 text-sm mr-2">@</span>
                  <input
                    type="text"
                    value={config.monitoring.slackNotifications.mentionUser || ''}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      monitoring: {
                        ...prev.monitoring,
                        slackNotifications: {
                          ...prev.monitoring.slackNotifications,
                          mentionUser: e.target.value.replace(/^@/, '')
                        }
                      }
                    }))}
                    placeholder="username"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Username to @mention for critical alerts (high error rates)
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Metrics */}
      <div>
        <label className="block text-sm font-medium text-gray-700">Metrics to Track</label>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="flex items-start">
            <div className="flex h-5 items-center">
              <input
                type="checkbox"
                checked={config.monitoring.metrics.responseTime}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    metrics: {
                      ...prev.monitoring.metrics,
                      responseTime: e.target.checked
                    }
                  }
                }))}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
            </div>
            <div className="ml-3">
              <label className="text-sm font-medium text-gray-700">Response Time</label>
              <p className="text-sm text-gray-500">Time from receiving message to sending reply</p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex h-5 items-center">
              <input
                type="checkbox"
                checked={config.monitoring.metrics.errorRate}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    metrics: {
                      ...prev.monitoring.metrics,
                      errorRate: e.target.checked
                    }
                  }
                }))}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
            </div>
            <div className="ml-3">
              <label className="text-sm font-medium text-gray-700">Error Rate</label>
              <p className="text-sm text-gray-500">Percentage of failed message deliveries</p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex h-5 items-center">
              <input
                type="checkbox"
                checked={config.monitoring.metrics.messageVolume}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    metrics: {
                      ...prev.monitoring.metrics,
                      messageVolume: e.target.checked
                    }
                  }
                }))}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
            </div>
            <div className="ml-3">
              <label className="text-sm font-medium text-gray-700">Message Volume</label>
              <p className="text-sm text-gray-500">Number of messages processed per day</p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex h-5 items-center">
              <input
                type="checkbox"
                checked={config.monitoring.metrics.aiConfidence}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    metrics: {
                      ...prev.monitoring.metrics,
                      aiConfidence: e.target.checked
                    }
                  }
                }))}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
            </div>
            <div className="ml-3">
              <label className="text-sm font-medium text-gray-700">AI Confidence</label>
              <p className="text-sm text-gray-500">AI's confidence in generated responses</p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex h-5 items-center">
              <input
                type="checkbox"
                checked={config.monitoring.metrics.customerSentiment}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    metrics: {
                      ...prev.monitoring.metrics,
                      customerSentiment: e.target.checked
                    }
                  }
                }))}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
            </div>
            <div className="ml-3">
              <label className="text-sm font-medium text-gray-700">Customer Sentiment</label>
              <p className="text-sm text-gray-500">Analysis of customer message sentiment</p>
            </div>
          </div>
        </div>
      </div>

      {/* Data Retention */}
      <div>
        <label className="block text-sm font-medium text-gray-700">Data Retention</label>
        <div className="mt-4 grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-600">Logs Retention</label>
            <div className="mt-1 flex items-center gap-2">
              <input
                type="number"
                min="1"
                max="365"
                value={config.monitoring.retention.logsRetentionDays}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    retention: {
                      ...prev.monitoring.retention,
                      logsRetentionDays: parseInt(e.target.value) || 30
                    }
                  }
                }))}
                className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
              <span className="text-sm text-gray-500">days</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              How long to keep system logs
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Message History</label>
            <div className="mt-1 flex items-center gap-2">
              <input
                type="number"
                min="1"
                max="365"
                value={config.monitoring.retention.messageHistoryDays}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  monitoring: {
                    ...prev.monitoring,
                    retention: {
                      ...prev.monitoring.retention,
                      messageHistoryDays: parseInt(e.target.value) || 90
                    }
                  }
                }))}
                className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
              <span className="text-sm text-gray-500">days</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              How long to keep message history
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSystemIntegrationStep = () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-medium text-gray-900">System Integration</h3>
        <p className="mt-1 text-sm text-gray-500">
          Connect your SMS automation with your existing business systems.
        </p>
      </div>

      {/* Zendesk Integration */}
      <div className="space-y-4">
        <div className="flex items-start">
          <div className="flex h-5 items-center">
            <input
              type="checkbox"
              checked={config.systemIntegration.zendesk.enabled}
              onChange={(e) => handleZendeskChange({ enabled: e.target.checked })}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
          </div>
          <div className="ml-3">
            <label className="text-sm font-medium text-gray-700">Zendesk Integration</label>
            <p className="text-sm text-gray-500">Create and update Zendesk tickets from SMS conversations</p>
          </div>
        </div>

        {config.systemIntegration.zendesk.enabled && (
          <div className="ml-7 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600">Email</label>
              <input
                type="email"
                value={config.systemIntegration.zendesk.email}
                onChange={(e) => handleZendeskChange({ email: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">API Token</label>
              <input
                type="password"
                value={config.systemIntegration.zendesk.apiToken}
                onChange={(e) => handleZendeskChange({ apiToken: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">Subdomain</label>
              <div className="mt-1 flex rounded-md shadow-sm">
                <span className="inline-flex items-center rounded-l-md border border-r-0 border-gray-300 bg-gray-50 px-3 text-gray-500 sm:text-sm">
                  https://
                </span>
                <input
                  type="text"
                  value={config.systemIntegration.zendesk.subdomain}
                  onChange={(e) => handleZendeskChange({ subdomain: e.target.value })}
                  placeholder="your-domain.zendesk.com"
                  className="block flex-1 rounded-none rounded-r-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.systemIntegration.zendesk.createTickets}
                  onChange={(e) => handleZendeskChange({ createTickets: e.target.checked })}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label className="ml-2 text-sm text-gray-600">Create tickets for new conversations</label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.systemIntegration.zendesk.updateExisting}
                  onChange={(e) => handleZendeskChange({ updateExisting: e.target.checked })}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label className="ml-2 text-sm text-gray-600">Update existing tickets</label>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Calendly Integration */}
      <div className="space-y-4">
        <div className="flex items-start">
          <div className="flex h-5 items-center">
            <input
              type="checkbox"
              checked={config.systemIntegration.calendly.enabled}
              onChange={(e) => handleCalendlyChange({ enabled: e.target.checked })}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
          </div>
          <div className="ml-3">
            <label className="text-sm font-medium text-gray-700">Calendly Integration</label>
            <p className="text-sm text-gray-500">Create and update Calendly events from SMS conversations</p>
          </div>
        </div>

        {config.systemIntegration.calendly.enabled && (
          <div className="ml-7 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600">Access Token</label>
              <input
                type="password"
                value={config.systemIntegration.calendly.access_token}
                onChange={(e) => handleCalendlyChange({ access_token: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">User URI</label>
              <input
                type="text"
                value={config.systemIntegration.calendly.user_uri}
                onChange={(e) => handleCalendlyChange({ user_uri: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">Webhook URI</label>
              <input
                type="url"
                value={config.systemIntegration.calendly.webhook_uri}
                onChange={(e) => handleCalendlyChange({ webhook_uri: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">Default Event Type</label>
              <input
                type="text"
                value={config.systemIntegration.calendly.default_event_type}
                onChange={(e) => handleCalendlyChange({ default_event_type: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">Booking Window Days</label>
              <input
                type="number"
                min="1"
                max="365"
                value={config.systemIntegration.calendly.booking_window_days}
                onChange={(e) => handleCalendlyChange({ booking_window_days: parseInt(e.target.value) || 14 })}
                className="mt-1 block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">Minimum Notice Hours</label>
              <input
                type="number"
                min="1"
                max="24"
                value={config.systemIntegration.calendly.min_notice_hours}
                onChange={(e) => handleCalendlyChange({ min_notice_hours: parseInt(e.target.value) || 4 })}
                className="mt-1 block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">Reminder Hours</label>
              <input
                type="text"
                value={config.systemIntegration.calendly.reminder_hours.join(',')}
                onChange={(e) => {
                  const reminderHours = e.target.value.split(',').map(Number);
                  handleCalendlyChange({ reminder_hours: reminderHours });
                }}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">SMS Notifications</label>
              <div className="mt-2 space-y-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={config.systemIntegration.calendly.sms_notifications.enabled}
                    onChange={(e) => handleCalendlyChange({ sms_notifications: { ...config.systemIntegration.calendly.sms_notifications, enabled: e.target.checked } })}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-600">Send SMS notifications for events</label>
                </div>

                {config.systemIntegration.calendly.sms_notifications.enabled && (
                  <div className="ml-6 space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-600">Include Cancel Link</label>
                      <div className="mt-1 flex items-center">
                        <input
                          type="checkbox"
                          checked={config.systemIntegration.calendly.sms_notifications.include_cancel_link}
                          onChange={(e) => handleCalendlyChange({ sms_notifications: { ...config.systemIntegration.calendly.sms_notifications, include_cancel_link: e.target.checked } })}
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 text-sm text-gray-600">Include cancel link in SMS notifications</label>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-600">Include Reschedule Link</label>
                      <div className="mt-1 flex items-center">
                        <input
                          type="checkbox"
                          checked={config.systemIntegration.calendly.sms_notifications.include_reschedule_link}
                          onChange={(e) => handleCalendlyChange({ sms_notifications: { ...config.systemIntegration.calendly.sms_notifications, include_reschedule_link: e.target.checked } })}
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 text-sm text-gray-600">Include reschedule link in SMS notifications</label>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-600">Confirmation Message</label>
                      <input
                        type="text"
                        value={config.systemIntegration.calendly.sms_notifications.confirmation_message}
                        onChange={(e) => handleCalendlyChange({ sms_notifications: { ...config.systemIntegration.calendly.sms_notifications, confirmation_message: e.target.value } })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-600">Reminder Message</label>
                      <input
                        type="text"
                        value={config.systemIntegration.calendly.sms_notifications.reminder_message}
                        onChange={(e) => handleCalendlyChange({ sms_notifications: { ...config.systemIntegration.calendly.sms_notifications, reminder_message: e.target.value } })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-600">Cancellation Message</label>
                      <input
                        type="text"
                        value={config.systemIntegration.calendly.sms_notifications.cancellation_message}
                        onChange={(e) => handleCalendlyChange({ sms_notifications: { ...config.systemIntegration.calendly.sms_notifications, cancellation_message: e.target.value } })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-600">Reschedule Message</label>
                      <input
                        type="text"
                        value={config.systemIntegration.calendly.sms_notifications.reschedule_message}
                        onChange={(e) => handleCalendlyChange({ sms_notifications: { ...config.systemIntegration.calendly.sms_notifications, reschedule_message: e.target.value } })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                checked={config.systemIntegration.calendly.allow_cancellation}
                onChange={(e) => handleCalendlyChange({ allow_cancellation: e.target.checked })}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-600">Allow Cancellation</label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                checked={config.systemIntegration.calendly.allow_rescheduling}
                onChange={(e) => handleCalendlyChange({ allow_rescheduling: e.target.checked })}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-600">Allow Rescheduling</label>
            </div>
          </div>
        )}
      </div>

      {/* Webhook Integration */}
      <div className="space-y-4">
        <div className="flex items-start">
          <div className="flex h-5 items-center">
            <input
              type="checkbox"
              checked={config.systemIntegration.webhook.enabled}
              onChange={(e) => handleWebhookChange({ enabled: e.target.checked })}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
          </div>
          <div className="ml-3">
            <label className="text-sm font-medium text-gray-700">Custom Webhook</label>
            <p className="text-sm text-gray-500">Send events to your own endpoint</p>
          </div>
        </div>

        {config.systemIntegration.webhook.enabled && (
          <div className="ml-7 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600">Webhook URL</label>
              <input
                type="url"
                value={config.systemIntegration.webhook.url}
                onChange={(e) => handleWebhookChange({ url: e.target.value })}
                placeholder="https://your-domain.com/webhook"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">Events to Send</label>
              <div className="mt-2 space-y-2">
                {['message.received', 'message.sent', 'message.failed', 'conversation.started', 'conversation.ended'].map((event) => (
                  <div key={event} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.systemIntegration.webhook.events.includes(event)}
                      onChange={(e) => {
                        const events = e.target.checked
                          ? [...config.systemIntegration.webhook.events, event]
                          : config.systemIntegration.webhook.events.filter(e => e !== event);
                        
                        handleWebhookChange({ events });
                      }}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-600">{event}</label>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="rounded-md bg-blue-50 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3 flex-1 md:flex md:justify-between">
            <p className="text-sm text-blue-700">
              Need to integrate with a different system? Contact us for custom integrations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTwilioConfigStep = () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Twilio Configuration</h3>
        <p className="mt-1 text-sm text-gray-500">
          Configure your Twilio account settings for SMS automation.
        </p>
      </div>

      {/* Core Twilio Settings */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-600">Account SID</label>
          <input
            type="password"
            value={config.twilio.accountSid}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              twilio: {
                ...prev.twilio,
                accountSid: e.target.value
              }
            }))}
            placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-xs text-gray-500">Find this in your Twilio Console</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600">Auth Token</label>
          <input
            type="password"
            value={config.twilio.authToken}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              twilio: {
                ...prev.twilio,
                authToken: e.target.value
              }
            }))}
            placeholder="your_auth_token"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-xs text-gray-500">Your Twilio account's auth token</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600">Phone Number</label>
          <input
            type="tel"
            value={config.twilio.phoneNumber}
            onChange={(e) => handlePhoneNumberChange(e.target.value)}
            placeholder="+1234567890"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-xs text-gray-500">Your Twilio phone number in E.164 format</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600">Messaging Service SID (Optional)</label>
          <input
            type="text"
            value={config.twilio.messagingServiceSid}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              twilio: {
                ...prev.twilio,
                messagingServiceSid: e.target.value
              }
            }))}
            placeholder="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-xs text-gray-500">If you're using a Messaging Service instead of a single phone number</p>
        </div>
      </div>

      {/* Advanced Settings */}
      <div>
        <h4 className="text-sm font-medium text-gray-900">Advanced Settings</h4>
        <div className="mt-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600">Webhook URL</label>
            <input
              type="url"
              value={config.twilio.webhookUrl}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                twilio: {
                  ...prev.twilio,
                  webhookUrl: e.target.value
                }
              }))}
              placeholder="https://your-domain.com/api/sms/webhook"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <p className="mt-1 text-xs text-gray-500">URL that Twilio will call when receiving messages</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Fallback URL (Optional)</label>
            <input
              type="url"
              value={config.twilio.fallbackUrl}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                twilio: {
                  ...prev.twilio,
                  fallbackUrl: e.target.value
                }
              }))}
              placeholder="https://your-domain.com/api/sms/fallback"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <p className="mt-1 text-xs text-gray-500">URL that Twilio will call if the primary webhook fails</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Status Callback URL (Optional)</label>
            <input
              type="url"
              value={config.twilio.statusCallback}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                twilio: {
                  ...prev.twilio,
                  statusCallback: e.target.value
                }
              }))}
              placeholder="https://your-domain.com/api/sms/status"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <p className="mt-1 text-xs text-gray-500">URL for receiving message delivery status updates</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Retry Count</label>
            <input
              type="number"
              min="0"
              max="10"
              value={config.twilio.retryCount}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                twilio: {
                  ...prev.twilio,
                  retryCount: parseInt(e.target.value) || 0
                }
              }))}
              className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <p className="mt-1 text-xs text-gray-500">Number of times to retry failed message deliveries (0-10)</p>
          </div>
        </div>
      </div>

      {/* Help Text */}
      <div className="rounded-md bg-blue-50 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Need help?</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc pl-5 space-y-1">
                <li>Find your Account SID and Auth Token in the <a href="https://www.twilio.com/console" target="_blank" rel="noopener noreferrer" className="underline">Twilio Console</a></li>
                <li>Phone numbers should be in E.164 format (e.g., +1234567890)</li>
                <li>Make sure your webhook URL is publicly accessible</li>
                <li>Consider using ngrok for local development</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep = () => {
    switch (step) {
      case 1:
        return renderTwilioConfigStep();
      case 2:
        return renderBrandToneStep();
      case 3:
        return renderAITrainingStep();
      case 4:
        return renderContextStep();
      case 5:
        return renderResponseStep();
      case 6:
        return renderMonitoringStep();
      case 7:
        return renderSystemIntegrationStep();
      default:
        return null;
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-900">
            Step {step} of 7
          </span>
          <span className="text-sm font-medium text-gray-500">
            {step === 1 && 'Twilio Configuration'}
            {step === 2 && 'Brand Tone & Style'}
            {step === 3 && 'AI Training'}
            {step === 4 && 'Contextual Understanding'}
            {step === 5 && 'Response Templates'}
            {step === 6 && 'Monitoring'}
            {step === 7 && 'System Integration'}
          </span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full">
          <div
            className="h-2 bg-indigo-600 rounded-full transition-all duration-500"
            style={{ width: `${(step / 7) * 100}%` }}
          />
        </div>
      </div>

      {/* Step content */}
      {renderStep()}

      {/* Navigation */}
      <div className="mt-8 flex justify-between">
        <button
          type="button"
          onClick={onCancel}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </button>
        <div className="space-x-3">
          {step > 1 && (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Previous
            </button>
          )}
          <button
            type="button"
            onClick={() => {
              if (step < 7) {
                setStep(step + 1);
              } else {
                onComplete(config);
              }
            }}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            {step === 7 ? 'Complete' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
}
