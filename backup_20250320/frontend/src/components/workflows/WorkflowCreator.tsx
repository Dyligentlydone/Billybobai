import { useState } from 'react';
import { useMutation } from 'react-query';
import toast from 'react-hot-toast';
import axios from 'axios';

interface WorkflowAnalysis {
  channels: string[];
  suggestedTemplates: {
    email?: Array<{
      name: string;
      subject: string;
      content: string;
    }>;
    sms?: Array<{
      name: string;
      content: string;
    }>;
  };
  estimatedCosts: {
    monthly: {
      sms: number;
      email: number;
      voice: number;
      whatsapp: number;
    };
  };
}

export default function WorkflowCreator() {
  const [input, setInput] = useState('');
  const [analysis, setAnalysis] = useState<WorkflowAnalysis | null>(null);

  const analyzeWorkflow = useMutation(
    async (input: string) => {
      const { data } = await axios.post('/api/workflows/analyze', { input });
      return data;
    },
    {
      onSuccess: (data) => {
        setAnalysis(data);
        toast.success('Workflow analyzed successfully!');
      },
      onError: () => {
        toast.error('Failed to analyze workflow');
      },
    }
  );

  const createWorkflow = useMutation(
    async (workflowData: any) => {
      const { data } = await axios.post('/api/workflows', workflowData);
      return data;
    },
    {
      onSuccess: () => {
        toast.success('Workflow created successfully!');
        setInput('');
        setAnalysis(null);
      },
      onError: () => {
        toast.error('Failed to create workflow');
      },
    }
  );

  const handleAnalyze = () => {
    if (!input.trim()) {
      toast.error('Please enter a workflow description');
      return;
    }
    analyzeWorkflow.mutate(input);
  };

  const handleCreate = () => {
    if (!analysis) return;

    createWorkflow.mutate({
      name: 'New Workflow', // This should be customizable
      naturalLanguageInput: input,
      channels: analysis.channels,
      configuration: {
        email: {
          templates: analysis.suggestedTemplates.email || []
        },
        sms: {
          templates: analysis.suggestedTemplates.sms || []
        }
      }
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <label
          htmlFor="workflow-input"
          className="block text-sm font-medium text-gray-700"
        >
          Describe your automation needs
        </label>
        <div className="mt-1">
          <textarea
            id="workflow-input"
            rows={4}
            className="shadow-sm block w-full sm:text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="e.g., CoffeeShop123 needs email automation for order confirmations and a chatbot on their website"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
        </div>
      </div>

      <div className="flex justify-end space-x-4">
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={analyzeWorkflow.isLoading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {analyzeWorkflow.isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {analysis && (
        <div className="mt-6 bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Analysis Results
            </h3>
            
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-500">Channels</h4>
              <div className="mt-2 flex space-x-2">
                {analysis.channels.map((channel) => (
                  <span
                    key={channel}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                  >
                    {channel}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-500">
                Estimated Monthly Costs
              </h4>
              <div className="mt-2 grid grid-cols-2 gap-4 sm:grid-cols-4">
                {Object.entries(analysis.estimatedCosts.monthly).map(
                  ([service, cost]) => (
                    <div key={service} className="bg-gray-50 p-3 rounded-lg">
                      <dt className="text-xs font-medium text-gray-500 uppercase">
                        {service}
                      </dt>
                      <dd className="mt-1 text-sm font-semibold text-gray-900">
                        ${cost.toFixed(2)}
                      </dd>
                    </div>
                  )
                )}
              </div>
            </div>

            <div className="mt-6">
              <button
                type="button"
                onClick={handleCreate}
                disabled={createWorkflow.isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                {createWorkflow.isLoading ? 'Creating...' : 'Create Workflow'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
