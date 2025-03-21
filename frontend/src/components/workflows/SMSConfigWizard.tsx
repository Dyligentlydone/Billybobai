import { useState } from 'react';

interface Props {
  onComplete: (config: any) => void;
  onCancel: () => void;
}

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

const INITIAL_CONFIG = {
  brandTone: {
    voiceType: 'professional' as const,
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
  }
};

export default function SMSConfigWizard({ onComplete, onCancel }: Props) {
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState(INITIAL_CONFIG);
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
                <label className="block text-sm font-medium text-gray-600 mb-1">Template Name</label>
                <input
                  type="text"
                  value={newTemplateName}
                  onChange={(e) => setNewTemplateName(e.target.value)}
                  placeholder="e.g., Order Status Update"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Variables</label>
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
              <label className="block text-sm font-medium text-gray-600 mb-1">Template Content</label>
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
              <label className="block text-sm font-medium text-gray-600 mb-1">When to Use</label>
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
                  {newTemplate.replace(/{(\w+)}/g, (match, variable) => 
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

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-900">
            Step {step} of 7
          </span>
          <span className="text-sm font-medium text-gray-500">
            {step === 1 && 'Brand Tone & Style'}
            {step === 2 && 'AI Training'}
            {step === 3 && 'Contextual Understanding'}
            {step === 4 && 'Response Templates'}
            {step === 5 && 'Monitoring'}
            {step === 6 && 'System Integration'}
            {step === 7 && 'Testing'}
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
      {step === 1 && renderBrandToneStep()}
      {step === 2 && renderAITrainingStep()}
      {step === 3 && renderContextStep()}
      {step === 4 && renderResponseStep()}

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
