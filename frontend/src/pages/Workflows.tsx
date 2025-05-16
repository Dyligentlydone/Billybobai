import { useState } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { AxiosError } from 'axios';
import api from '../services/api';
import toast from 'react-hot-toast';
import WorkflowBuilder from '../components/workflows/WorkflowBuilder';
import SMSConfigWizard from '../components/workflows/SMSConfigWizard';
import EmailConfigWizard from '../components/workflows/EmailConfigWizard';
import { VoiceWizard } from '../components/wizard/VoiceWizard';
import { WizardProvider } from '../contexts/WizardContext';
import { Dialog, DialogContent, DialogActions, Button } from '@mui/material';

// Helper function to generate UUID
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Use the global API service from '../services/api'
// This ensures consistent HTTPS protocol usage and prevents mixed content errors

type WorkflowStatus = 'DRAFT' | 'ACTIVE' | 'ARCHIVED';

interface Workflow {
  _id: string;
  name: string;
  status: WorkflowStatus;
  createdAt: string;
  updatedAt: string;
  [key: string]: any; // To allow for additional properties
}

const Workflows: React.FC = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [selectedWorkflowData, setSelectedWorkflowData] = useState<any>(null);
  const [showSMSWizard, setShowSMSWizard] = useState(false);
  const [showEmailWizard, setShowEmailWizard] = useState(false);
  const [showVoiceWizard, setShowVoiceWizard] = useState(false);
  // Removed smsConfig state as it's not needed and may cause duplicate workflow creation
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editingWorkflowId, setEditingWorkflowId] = useState<string | null>(null);

  // Initialize the query client for cache invalidation
  const queryClient = useQueryClient();

  const fetchWorkflows = async () => {
    try {
      console.log('Fetching workflows from API');
      // Use the axios instance with proper credential handling
      const response = await api.get('/api/workflows');
      
      // Enhanced logging to debug the response
      console.log('Workflows raw response:', response);
      console.log('Workflows data type:', typeof response.data);
      console.log('Is array?', Array.isArray(response.data));
      
      if (!response.data) {
        console.error('Empty response data');
        return [];
      }
      
      if (!Array.isArray(response.data)) {
        console.error('Response is not an array:', response.data);
        // Try to convert non-array response to array if possible
        if (typeof response.data === 'object') {
          console.log('Attempting to convert object to array');
          return [response.data].map(workflow => ({
            ...workflow,
            status: (workflow.status || '').toUpperCase() as WorkflowStatus
          }));
        }
        return [];
      }
      
      // If we get here, we have an array response
      console.log('Workflows count:', response.data.length);
      return response.data.map(workflow => ({
        ...workflow,
        // Normalize status values to match UI expectations
        status: (workflow.status || '').toUpperCase() as WorkflowStatus
      }));
    } catch (err) {
      console.error('Error fetching workflows:', err);
      // Return empty array instead of throwing to prevent UI breakage
      return [];
    }
  };

  const { data: workflows, isLoading, error } = useQuery<Workflow[], AxiosError>(
    'workflows',
    fetchWorkflows,
    {
      retry: 3,
      retryDelay: 1000,
    }
  );

  const handleSMSConfigComplete = (config: any) => {
    // Fix the structure mismatch - check both possible locations for twilio data
    // This makes the component more robust to different data structures
    const twilioConfig = config.twilio || {};
    const integrationConfig = config.integration || {};
    
    // Get the phone number from either location
    const phoneNumber = twilioConfig.phoneNumber || 
                         twilioConfig.twilioPhoneNumber || 
                         integrationConfig.twilioPhoneNumber || 
                         integrationConfig.phoneNumber || '';
    
    // Get voice type from the right location
    const voiceType = (config.brandTone || {}).voiceType || 'professional';
    const greetings = (config.brandTone || {}).greetings || [];
    const wordsToAvoid = (config.brandTone || {}).wordsToAvoid || [];
    const businessHours = ((config.templates || {}).businessHours) || '{}';
    
    // Create workflow data that will be sent to the API
    // Determine if we're editing an existing workflow
    const isEditing = editingWorkflowId !== null;
    const workflowId = isEditing ? editingWorkflowId : generateUUID();
    
    // Make sure we get the business ID from the right place
    // Priority: 1. Direct business_id from config, 2. Existing workflow data, 3. Twilio config, 4. Default
    let businessId;
    if (config.business_id) {
      // If the SMSConfigWizard provided a top-level business_id, use that
      businessId = config.business_id;
      console.log('Using business ID from normalized config:', businessId);
    } else if (isEditing && selectedWorkflowData) {
      // If editing, get from the original workflow data
      businessId = selectedWorkflowData.business_id || selectedWorkflowData.client_id || '1';
      console.log('Using business ID from existing workflow:', businessId);
    } else {
      // Last resort: use from the form input or default to 1
      businessId = config.twilio.businessId || '1';
      console.log('Using business ID from form input:', businessId);
    }
    
    // Ensure it's a proper number/string (not an object or other type)
    businessId = typeof businessId === 'object' ? JSON.stringify(businessId) : String(businessId);
    console.log('Final normalized business ID:', businessId);
    
    // Preserve existing workflow name if editing
    let workflowName = 'SMS Workflow';
    if (isEditing && selectedWorkflowData && selectedWorkflowData.name) {
      workflowName = selectedWorkflowData.name;
    }
    
    console.log(`${isEditing ? 'Updating' : 'Creating'} workflow with ID: ${workflowId} and business ID: ${businessId}`);
                           
    // Construct the workflow data
    const workflowData = {
      workflow_id: workflowId,
      business_id: businessId,
      name: workflowName,
      type: 'sms',
      twilio: {
        type: 'sms',
        aiEnabled: 'true',
        phoneNumber: phoneNumber,
        prompt: `You are an AI assistant for ${voiceType} communication via SMS. Guidelines:
          - Voice: ${voiceType}
          - Greetings: ${greetings.join(', ')}
          - Avoid: ${wordsToAvoid.join(', ')}
          - Response time target: 5 seconds
          - Keep responses under 160 characters when possible
          - Use fallback message if unable to respond
          - Respect business hours: ${JSON.stringify(businessHours)}`,
      },
      actions: config // Include the full configuration
    };
    
    // Make the API call - use PUT for updates, POST for new workflows
    const apiCall = isEditing 
      ? api.put(`/api/workflows/${workflowId}`, workflowData) 
      : api.post('/api/workflows', workflowData);
    
    apiCall
      .then(response => {
        toast.success(`SMS workflow ${isEditing ? 'updated' : 'created'} successfully!`);
        queryClient.invalidateQueries('workflows'); // Refresh the list
        // Clear editing state
        setEditingWorkflowId(null);
        setSelectedWorkflowData(null);
        // IMPORTANT: Close the dialog first before any state changes that might trigger other effects
        setShowSMSWizard(false);
      })
      .catch(error => {
        toast.error(`Failed to ${isEditing ? 'update' : 'create'} SMS workflow`);
        console.error(`Error ${isEditing ? 'updating' : 'creating'} workflow:`, error);
        setShowSMSWizard(false);
      });
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
      const { data } = await api.get(`/api/workflows/${id}`);
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
      
      // Store the workflow ID being edited
      setEditingWorkflowId(id);
      console.log("Set editing workflow ID to:", id);
      
      // Extract and log business ID for debugging
      const businessId = workflowData.business_id || workflowData.client_id || null;
      console.log("Workflow business ID:", businessId);
      
      // Check workflow type to determine which editor to show
      if (workflowData.name && workflowData.name.toLowerCase().includes('sms')) {
        console.log("Loading SMS workflow in SMSConfigWizard");
        // Make sure we're passing all the data clearly
        setSelectedWorkflowData({
          ...workflowData,
          // Ensure these IDs are clearly available
          business_id: businessId,
          client_id: businessId,
          id: id
        });
        setShowSMSWizard(true);
      } else {
        console.log("Loading workflow in WorkflowBuilder");
        setSelectedWorkflow(id);
      }
    } catch (error) {
      console.error("Error editing workflow:", error);
      toast.error("Failed to load workflow for editing");
      // Clear editing state on error
      setEditingWorkflowId(null);
    }
  };

  // Add function to handle workflow deletion
  const handleDeleteWorkflow = async (id: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) {
      return;
    }
    
    try {
      console.log("Deleting workflow with ID:", id);
      
      const response = await api.delete(`/api/workflows/${id}`);
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
        />
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {selectedWorkflow ? (
        <WorkflowBuilder
          workflowId={selectedWorkflow}
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
                  ) : workflows && workflows.length > 0 ? (
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
                  ) : (
                    <div className="p-4 text-center text-sm text-gray-700">
                      No custom workflows yet. Create your first one or use a template above!
                    </div>
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
