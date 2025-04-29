import { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { listClients, updateClient, listBusinesses, Client } from '../services/api';
import { useBusiness } from '../contexts/BusinessContext';
import ClientPermissionsModal from '../components/ClientPermissionsModal';

export default function Clients() {
  const { selectedBusinessId, setSelectedBusinessId, isAdmin } = useBusiness();
  const queryClient = useQueryClient();
  const [modalClient, setModalClient] = useState<Client | null>(null);

  const { data: clients = [], isLoading, refetch } = useQuery(['clients', selectedBusinessId], async () => {
    if (!selectedBusinessId) return [];
    return listClients(selectedBusinessId);
  }, {
    enabled: Boolean(selectedBusinessId),
  });

  const { data: businesses = [] } = useQuery(['businesses'], listBusinesses, {
    enabled: isAdmin,
  });

  const [search, setSearch] = useState('');

  const updateMutation = useMutation(
    ({ id, perms, passcode, nickname }: { id: number; perms: any; passcode: string; nickname: string }) =>
      updateClient(id, { permissions: perms, passcode, nickname }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['clients', selectedBusinessId]);
        setModalClient(null);
      },
    },
  );

  if (isAdmin && !selectedBusinessId) {
    return (
      <div className="space-y-4">
        <h2 className="text-lg font-medium">Select Business</h2>
        <select
          className="rounded-md border p-2"
          onChange={(e) => setSelectedBusinessId(e.target.value || null)}
          defaultValue=""
        >
          <option value="" disabled>
            -- choose business --
          </option>
          {businesses.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Clients</h1>
          <p className="mt-2 text-sm text-gray-700">Manage your client accounts and their settings.</p>
        </div>
      </div>

      <div className="mt-4">
        <input
          type="text"
          className="w-full rounded-md border p-2"
          placeholder="Search passcode…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <p>Loading…</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Passcode</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Nickname</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {clients
                .filter((c) => c.passcode.includes(search) || (c.nickname || '').toLowerCase().includes(search.toLowerCase()))
                .map((client) => (
                  <tr key={client.id}>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">{client.passcode}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">{client.nickname || '-'}</td>
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
        onSave={(p, passcode, nickname) => {
          if (modalClient) {
            updateMutation.mutate({ id: modalClient.id, perms: p, passcode, nickname });
          }
        }}
      />
    </div>
  );
}
