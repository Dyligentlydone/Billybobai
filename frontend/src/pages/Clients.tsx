import { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { listClients, updateClientPermissions, Client } from '../services/api';
import { useBusiness } from '../contexts/BusinessContext';
import ClientPermissionsModal from '../components/ClientPermissionsModal';

export default function Clients() {
  const { selectedBusinessId } = useBusiness();
  const queryClient = useQueryClient();
  const [modalClient, setModalClient] = useState<Client | null>(null);

  const { data: clients = [], isLoading, refetch } = useQuery(['clients', selectedBusinessId], async () => {
    if (!selectedBusinessId) return [];
    return listClients(selectedBusinessId);
  }, {
    enabled: Boolean(selectedBusinessId),
  });

  const updateMutation = useMutation(
    ({ id, permissions }: { id: number; permissions: any }) => updateClientPermissions(id, permissions),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['clients', selectedBusinessId]);
        setModalClient(null);
      },
    },
  );

  if (!selectedBusinessId) {
    return <p>Please select a business first.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Clients</h1>
          <p className="mt-2 text-sm text-gray-700">Manage your client accounts and their settings.</p>
        </div>
      </div>

      {isLoading ? (
        <p>Loading…</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Passcode</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {clients.map((client) => (
                <tr key={client.id}>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">{client.passcode}</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm">
                    <button
                      onClick={() => setModalClient(client)}
                      className="rounded-md bg-indigo-600 px-3 py-1 text-white hover:bg-indigo-700"
                    >
                      Edit permissions
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ClientPermissionsModal
        client={modalClient}
        open={Boolean(modalClient)}
        onClose={() => setModalClient(null)}
        onSave={(perms) => {
          if (modalClient) {
            updateMutation.mutate({ id: modalClient.id, permissions: perms });
          }
        }}
      />
    </div>
  );
}
