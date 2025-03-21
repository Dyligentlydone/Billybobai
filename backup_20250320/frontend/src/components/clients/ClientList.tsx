import { useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

interface Client {
  _id: string;
  name: string;
  twilioConfig: {
    accountSid?: string;
    phoneNumber?: string;
  };
  sendgridConfig: {
    senderEmail?: string;
  };
  zendeskConfig: {
    subdomain?: string;
    email?: string;
  };
}

interface ClientListProps {
  clients: Client[];
  onEdit: (client: Client) => void;
}

export default function ClientList({ clients, onEdit }: ClientListProps) {
  const queryClient = useQueryClient();

  const validateMutation = useMutation(
    async (clientId: string) => {
      const { data } = await axios.post(`/api/clients/${clientId}/validate`);
      return data;
    },
    {
      onSuccess: (data) => {
        const results = [];
        if (data.twilio) results.push('Twilio');
        if (data.sendgrid) results.push('SendGrid');
        if (data.zendesk) results.push('Zendesk');
        
        if (results.length > 0) {
          toast.success(`Valid credentials for: ${results.join(', ')}`);
        } else {
          toast.error('No valid credentials found');
        }
      },
      onError: () => {
        toast.error('Failed to validate credentials');
      }
    }
  );

  const deleteMutation = useMutation(
    async (clientId: string) => {
      await axios.delete(`/api/clients/${clientId}`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('clients');
        toast.success('Client deleted successfully');
      },
      onError: () => {
        toast.error('Failed to delete client');
      }
    }
  );

  const handleValidate = (clientId: string) => {
    validateMutation.mutate(clientId);
  };

  const handleDelete = (clientId: string) => {
    if (window.confirm('Are you sure you want to delete this client?')) {
      deleteMutation.mutate(clientId);
    }
  };

  return (
    <div className="mt-8 flex flex-col">
      <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                    Name
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Twilio
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    SendGrid
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Zendesk
                  </th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {clients.map((client) => (
                  <tr key={client._id}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                      {client.name}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {client.twilioConfig.accountSid ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Configured
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Not Set
                        </span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {client.sendgridConfig.senderEmail ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Configured
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Not Set
                        </span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {client.zendeskConfig.subdomain ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Configured
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Not Set
                        </span>
                      )}
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <div className="flex justify-end space-x-3">
                        <button
                          onClick={() => handleValidate(client._id)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Validate
                        </button>
                        <button
                          onClick={() => onEdit(client)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(client._id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
