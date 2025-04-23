import { useState } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import axios, { AxiosError } from 'axios';
import toast from 'react-hot-toast';
import WorkflowBuilder from '../components/workflows/WorkflowBuilder';
import SMSConfigWizard from '../components/workflows/SMSConfigWizard';
import EmailConfigWizard from '../components/workflows/EmailConfigWizard';
import { VoiceWizard } from '../components/wizard/VoiceWizard';
import { WizardProvider } from '../contexts/WizardContext';
import { Dialog, DialogContent, DialogActions, Button } from '@mui/material';

interface Workflow {
  _id: string;
  name: string;
  status: 'active' | 'draft' | 'archived';
  createdAt: string;
  updatedAt: string;
}

const API_URL = import.meta.env.VITE_BACKEND_URL || 'https://billybobai-production.up.railway.app';

const Workflows: React.FC = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [selectedWorkflowData, setSelectedWorkflowData] = useState<any>(null);
  const [showSMSWizard, setShowSMSWizard] = useState(false);
  const [showEmailWizard, setShowEmailWizard] = useState(false);
  const [showVoiceWizard, setShowVoiceWizard] = useState(false);
  const [smsConfig, setSMSConfig] = useState<any>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // Initialize the query client for cache invalidation
  const queryClient = useQueryClient();

  const { data: workflows, isLoading, error } = useQuery<Workflow[], AxiosError>(
    'workflows',
    async () => {
      try {
        const { data } = await axios.get(`${API_URL}/api/workflows`);
        return data;
      } catch (err) {
        console.error('Error fetching workflows:', err);
        throw err;
      }
    },
    {
      retry: 3,
      retryDelay: 1000,
    }
  );

  const handleSMSConfigComplete = (config: any) => {
    setSMSConfig({
      twilio: {
        type: 'sms',
        aiEnabled: 'true',
        phoneNumber: config.integration.twilioPhoneNumber,
        prompt: `You are an AI assistant for ${config.brandTone.voiceType} communication via SMS. Guidelines:
          - Voice: ${config.brandTone.voiceType}
          - Greetings: ${config.brandTone.greetings.join(', ')}
          - Avoid: ${config.brandTone.wordsToAvoid.join(', ')}
          - Response time target: 5 seconds
          - Keep responses under 160 characters when possible
          - Use fallback message if unable to respond
          - Respect business hours: ${JSON.stringify(config.templates.businessHours)}`,
      },
      instructions: [
        'Configure Twilio webhook URL',
        'Set up monitoring alerts',
        'Test with sample messages',
        'Enable production mode when ready'
      ]
    });
    setShowSMSWizard(false);
    setIsCreating(true);
  };

  const handleEmailConfigComplete = () => {
    setShowEmailWizard(false);
    setIsCreating(true);
  };

  const handleVoiceConfigComplete = () => {
    setShowVoiceWizard(false);
    setIsCreating(true);
  };

  const fetchWorkflowData = async (id: string) => {
    try {
      const { data } = await axios.get(`${API_URL}/api/workflows/${id}`);
      console.log("Fetched workflow data:", data);
      return data;
    } catch (err) {
      console.error('Error fetching workflow data:', err);
      throw err;
    }
  };

  const handleEditWorkflow = async (id: string) => {
    try {
      console.log("Fetching workflow data for ID:", id);
      const workflowData = await fetchWorkflowData(id);
      console.log("Received workflow data:", JSON.stringify(workflowData, null, 2));
      
      // Check workflow type to determine which editor to show
      if (workflowData.name && workflowData.name.toLowerCase().includes('sms')) {
        console.log("Loading SMS workflow in SMSConfigWizard");
        setSelectedWorkflowData(workflowData);
        setShowSMSWizard(true);
      } else {
        console.log("Loading workflow in WorkflowBuilder");
        setSelectedWorkflow(id);
      }
    } catch (error) {
      console.error("Error editing workflow:", error);
    }
  };

  // Add function to handle workflow deletion
  const handleDeleteWorkflow = async (id: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) {
      return;
    }
    
    try {
      console.log("Deleting workflow with ID:", id);
      
      const response = await axios.delete(`${API_URL}/api/workflows/${id}`);
      console.log("Delete response:", response.status);
      
      if (response.status === 204) {
        // Refetch the workflows list to update the UI
        queryClient.invalidateQueries('workflows');
        toast.success('Workflow deleted successfully');
      }
    } catch (error) {
      console.error("Error deleting workflow:", error);
      toast.error('Failed to delete workflow');
    }
  };

  if (showSMSWizard) {
    return (
      <div className="space-y-6">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">
              Configure SMS Automation
            </h1>
            <p className="mt-2 text-sm text-gray-700">
              Set up your automated SMS response system with AI-powered capabilities.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
            <button
              type="button"
              onClick={() => setShowSMSWizard(false)}
              className="inline-flex items-center justify-center rounded-md border border-transparent bg-gray-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 sm:w-auto"
            >
              Back to Workflows
            </button>
          </div>
        </div>
        <SMSConfigWizard
          onComplete={handleSMSConfigComplete}
          onCancel={() => setShowSMSWizard(false)}
          existingData={selectedWorkflowData}
        />
      </div>
    );
  }

  if (showEmailWizard) {
    return (
      <div className="space-y-6">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">
              Configure Email Automation
            </h1>
            <p className="mt-2 text-sm text-gray-700">
              Set up your automated email response system with AI-powered capabilities.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
            <button
              type="button"
              onClick={() => setShowEmailWizard(false)}
              className="inline-flex items-center justify-center rounded-md border border-transparent bg-gray-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 sm:w-auto"
            >
              Back to Workflows
            </button>
          </div>
        </div>
        <EmailConfigWizard
          onComplete={handleEmailConfigComplete}
          onCancel={() => setShowEmailWizard(false)}
        />
      </div>
    );
  }

  if (showVoiceWizard) {
    return (
      <Dialog
        open={showVoiceWizard}
        onClose={() => setShowVoiceWizard(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent>
          <WizardProvider>
            <VoiceWizard
              onComplete={handleVoiceConfigComplete}
              onCancel={() => setShowVoiceWizard(false)}
            />
          </WizardProvider>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowVoiceWizard(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    );
  }

  if (isCreating || selectedWorkflow) {
    return (
      <div className="space-y-6">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">
              {isCreating ? 'Create Workflow' : 'Edit Workflow'}
            </h1>
            <p className="mt-2 text-sm text-gray-700">
              {isCreating
                ? 'Create a new workflow by adding and connecting nodes.'
                : 'Edit your existing workflow by modifying nodes and connections.'}
            </p>
          </div>
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
            <button
              type="button"
              onClick={() => {
                setSelectedWorkflow(null);
                setIsCreating(false);
              }}
              className="inline-flex items-center justify-center rounded-md border border-transparent bg-gray-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 sm:w-auto"
            >
              Back to Workflows
            </button>
          </div>
        </div>
        <WorkflowBuilder
          workflowId={selectedWorkflow || undefined}
          smsConfig={smsConfig}
        />
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {selectedWorkflow ? (
        <WorkflowBuilder
          workflowId={selectedWorkflow}
          smsConfig={smsConfig}
        />
      ) : (
        <>
          <div className="sm:flex sm:items-center">
            <div className="sm:flex-auto">
              <h1 className="text-xl font-semibold text-gray-900">Workflows</h1>
              <p className="mt-2 text-sm text-gray-700">
                Create and manage automated workflows for your business communications.
              </p>
            </div>
            <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
              <button
                type="button"
                onClick={() => setIsCreating(true)}
                className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
              >
                Create Custom Workflow
              </button>
            </div>
          </div>

          {/* Template Cards */}
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-8">
            {/* SMS Automation Card */}
            <div className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
              <div className="flex-1 min-w-0">
                <button
                  onClick={() => setShowSMSWizard(true)}
                  className="focus:outline-none w-full text-left"
                >
                  <span className="absolute inset-0" aria-hidden="true" />
                  <p className="text-sm font-medium text-gray-900">SMS Automation</p>
                  <p className="text-sm text-gray-500 truncate">
                    Configure automated SMS responses
                  </p>
                </button>
              </div>
            </div>

            {/* Email Automation Card */}
            <div className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
              <div className="flex-1 min-w-0">
                <button
                  onClick={() => setShowEmailWizard(true)}
                  className="focus:outline-none w-full text-left"
                >
                  <span className="absolute inset-0" aria-hidden="true" />
                  <p className="text-sm font-medium text-gray-900">Email Automation</p>
                  <p className="text-sm text-gray-500 truncate">
                    Configure automated email responses
                  </p>
                </button>
              </div>
            </div>

            {/* Voice Call Automation Card */}
            <div className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
              <div className="flex-1 min-w-0">
                <button
                  onClick={() => setShowVoiceWizard(true)}
                  className="focus:outline-none w-full text-left"
                >
                  <span className="absolute inset-0" aria-hidden="true" />
                  <p className="text-sm font-medium text-gray-900">Voice Call Automation</p>
                  <p className="text-sm text-gray-500 truncate">
                    Configure automated voice responses
                  </p>
                </button>
              </div>
            </div>
          </div>

          <div className="mt-8 flex flex-col">
            <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                  {isLoading ? (
                    <div className="p-4 text-center text-sm text-gray-700">
                      Loading workflows...
                    </div>
                  ) : error ? (
                    <div className="p-4 text-center text-sm text-red-700">
                      Error loading workflows: {error.message}
                    </div>
                  ) : !workflows?.length ? (
                    <div className="p-4 text-center text-sm text-gray-700">
                      No custom workflows yet. Create your first one or use a template above!
                    </div>
                  ) : (
                    <table className="min-w-full divide-y divide-gray-300">
                      <thead className="bg-gray-50">
                        <tr>
                          <th
                            scope="col"
                            className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6"
                          >
                            Name
                          </th>
                          <th
                            scope="col"
                            className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                          >
                            Status
                          </th>
                          <th
                            scope="col"
                            className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                          >
                            Created
                          </th>
                          <th
                            scope="col"
                            className="relative py-3.5 pl-3 pr-4 sm:pr-6"
                          >
                            <span className="sr-only">Edit</span>
                          </th>
                          <th
                            scope="col"
                            className="relative py-3.5 pl-3 pr-4 sm:pr-6"
                          >
                            <span className="sr-only">Delete</span>
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 bg-white">
                        {workflows.map((workflow) => (
                          <tr key={workflow._id}>
                            <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                              {workflow.name}
                            </td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                              {workflow.status}
                            </td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                              {new Date(workflow.createdAt).toLocaleDateString()}
                            </td>
                            <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                              <button
                                onClick={() => handleEditWorkflow(workflow._id)}
                                className="text-indigo-600 hover:text-indigo-900"
                              >
                                Edit
                              </button>
                            </td>
                            <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                              <button
                                onClick={() => handleDeleteWorkflow(workflow._id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Wizards */}
      <Dialog open={showSMSWizard} onClose={() => setShowSMSWizard(false)} maxWidth="md" fullWidth>
        <DialogContent>
          <WizardProvider>
            <SMSConfigWizard
              onComplete={handleSMSConfigComplete}
              onCancel={() => setShowSMSWizard(false)}
              existingData={selectedWorkflowData}
            />
          </WizardProvider>
        </DialogContent>
      </Dialog>

      <Dialog open={showEmailWizard} onClose={() => setShowEmailWizard(false)} maxWidth="md" fullWidth>
        <DialogContent>
          <WizardProvider>
            <EmailConfigWizard
              onComplete={handleEmailConfigComplete}
              onCancel={() => setShowEmailWizard(false)}
            />
          </WizardProvider>
        </DialogContent>
      </Dialog>

      <Dialog open={showVoiceWizard} onClose={() => setShowVoiceWizard(false)} maxWidth="md" fullWidth>
        <DialogContent>
          <WizardProvider>
            <VoiceWizard
              onComplete={handleVoiceConfigComplete}
              onCancel={() => setShowVoiceWizard(false)}
            />
          </WizardProvider>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Workflows;
