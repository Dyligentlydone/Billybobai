import { useState } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

interface ClientFormProps {
  onSuccess?: () => void;
  initialData?: any;
  isEdit?: boolean;
}

export default function ClientForm({ onSuccess, initialData, isEdit }: ClientFormProps) {
  const [formData, setFormData] = useState({
    name: initialData?.name || '',
    twilioConfig: {
      accountSid: initialData?.twilioConfig?.accountSid || '',
      authToken: '',
      phoneNumber: initialData?.twilioConfig?.phoneNumber || ''
    },
    sendgridConfig: {
      apiKey: '',
      senderEmail: initialData?.sendgridConfig?.senderEmail || ''
    },
    zendeskConfig: {
      subdomain: initialData?.zendeskConfig?.subdomain || '',
      email: initialData?.zendeskConfig?.email || '',
      apiToken: ''
    }
  });

  const queryClient = useQueryClient();

  const mutation = useMutation(
    async (data: typeof formData) => {
      if (isEdit && initialData?._id) {
        const { data: response } = await axios.put(`/api/clients/${initialData._id}`, data);
        return response;
      } else {
        const { data: response } = await axios.post('/api/clients', data);
        return response;
      }
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('clients');
        toast.success(`Client ${isEdit ? 'updated' : 'created'} successfully!`);
        onSuccess?.();
      },
      onError: () => {
        toast.error(`Failed to ${isEdit ? 'update' : 'create'} client`);
      }
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const handleChange = (section: string, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [field]: value
      }
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Information */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Client Name
          </label>
          <input
            type="text"
            name="name"
            id="name"
            required
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
      </div>

      {/* Twilio Configuration */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Twilio Configuration</h3>
        <div className="space-y-4">
          <div>
            <label htmlFor="twilioAccountSid" className="block text-sm font-medium text-gray-700">
              Account SID
            </label>
            <input
              type="text"
              id="twilioAccountSid"
              value={formData.twilioConfig.accountSid}
              onChange={(e) => handleChange('twilioConfig', 'accountSid', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="twilioAuthToken" className="block text-sm font-medium text-gray-700">
              Auth Token
            </label>
            <input
              type="password"
              id="twilioAuthToken"
              value={formData.twilioConfig.authToken}
              onChange={(e) => handleChange('twilioConfig', 'authToken', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder={isEdit ? '••••••••' : ''}
            />
          </div>
          <div>
            <label htmlFor="twilioPhoneNumber" className="block text-sm font-medium text-gray-700">
              Phone Number
            </label>
            <input
              type="text"
              id="twilioPhoneNumber"
              value={formData.twilioConfig.phoneNumber}
              onChange={(e) => handleChange('twilioConfig', 'phoneNumber', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="+1234567890"
            />
          </div>
        </div>
      </div>

      {/* SendGrid Configuration */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">SendGrid Configuration</h3>
        <div className="space-y-4">
          <div>
            <label htmlFor="sendgridApiKey" className="block text-sm font-medium text-gray-700">
              API Key
            </label>
            <input
              type="password"
              id="sendgridApiKey"
              value={formData.sendgridConfig.apiKey}
              onChange={(e) => handleChange('sendgridConfig', 'apiKey', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder={isEdit ? '••••••••' : ''}
            />
          </div>
          <div>
            <label htmlFor="sendgridSenderEmail" className="block text-sm font-medium text-gray-700">
              Sender Email
            </label>
            <input
              type="email"
              id="sendgridSenderEmail"
              value={formData.sendgridConfig.senderEmail}
              onChange={(e) => handleChange('sendgridConfig', 'senderEmail', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {/* Zendesk Configuration */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Zendesk Configuration</h3>
        <div className="space-y-4">
          <div>
            <label htmlFor="zendeskSubdomain" className="block text-sm font-medium text-gray-700">
              Subdomain
            </label>
            <input
              type="text"
              id="zendeskSubdomain"
              value={formData.zendeskConfig.subdomain}
              onChange={(e) => handleChange('zendeskConfig', 'subdomain', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="your-subdomain"
            />
          </div>
          <div>
            <label htmlFor="zendeskEmail" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              id="zendeskEmail"
              value={formData.zendeskConfig.email}
              onChange={(e) => handleChange('zendeskConfig', 'email', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="zendeskApiToken" className="block text-sm font-medium text-gray-700">
              API Token
            </label>
            <input
              type="password"
              id="zendeskApiToken"
              value={formData.zendeskConfig.apiToken}
              onChange={(e) => handleChange('zendeskConfig', 'apiToken', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder={isEdit ? '••••••••' : ''}
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="submit"
          disabled={mutation.isLoading}
          className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          {mutation.isLoading ? 'Saving...' : isEdit ? 'Update Client' : 'Create Client'}
        </button>
      </div>
    </form>
  );
}
