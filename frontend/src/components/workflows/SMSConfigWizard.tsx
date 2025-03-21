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

const INITIAL_CONFIG = {
  brandTone: {
    voiceType: 'professional' as const,
    greetings: [],
    phrasingExamples: [],
    wordsToAvoid: []
  }
};

export default function SMSConfigWizard({ onComplete, onCancel }: Props) {
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState(INITIAL_CONFIG);
  const [newGreeting, setNewGreeting] = useState('');
  const [newPhrase, setNewPhrase] = useState('');
  const [newWordToAvoid, setNewWordToAvoid] = useState('');

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

  const removeItem = (array: string[], index: number, field: keyof BrandToneConfig) => {
    setConfig(prev => ({
      ...prev,
      brandTone: {
        ...prev.brandTone,
        [field]: array.filter((_, i) => i !== index)
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
