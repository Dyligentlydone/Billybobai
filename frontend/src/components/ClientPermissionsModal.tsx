import React, { useEffect, useState } from 'react';
import { Client } from '../services/api';
import {
  BusinessPermissions,
  DEFAULT_PERMISSIONS,
  convertFlattenedPermissions,
} from '../utils/permissions';

interface Props {
  client: Client | null;
  open: boolean;
  onClose: () => void;
  onSave: (perms: BusinessPermissions, passcode: string, nickname: string) => void;
}

/**
 * A lightweight permissions editor. It renders checkboxes for every boolean in
 * {@link DEFAULT_PERMISSIONS}, storing edits in local component state.
 */
export default function ClientPermissionsModal({ client, open, onClose, onSave }: Props) {
  const [perms, setPerms] = useState<BusinessPermissions>(DEFAULT_PERMISSIONS);
  const [localPasscode, setLocalPasscode] = useState(client?.passcode || '');
  const [nickname, setNickname] = useState(client?.nickname || '');

  // Sync when client changes or modal opens
  useEffect(() => {
    if (client) {
      try {
        console.log("Raw client permissions:", client.permissions);
        // Handle if permissions is a string (JSON string)
        let permissionsObj = client.permissions;
        if (typeof permissionsObj === 'string') {
          try {
            permissionsObj = JSON.parse(permissionsObj);
          } catch (e) {
            console.error("Failed to parse permissions string:", e);
            permissionsObj = {};
          }
        }
        const p = convertFlattenedPermissions(permissionsObj || {});
        console.log("Converted permissions:", p);
        // Merge with defaults so we always have full shape
        setPerms(p);
      } catch {
        setPerms(DEFAULT_PERMISSIONS);
      }
    }
  }, [client]);

  useEffect(() => {
    setLocalPasscode(client?.passcode || '');
    setNickname(client?.nickname || '');
  }, [client]);

  if (!open || !client) return null;

  const toggleNav = (key: keyof typeof perms.navigation) => {
    setPerms((prev) => ({
      ...prev,
      navigation: { ...prev.navigation, [key]: !prev.navigation[key] },
    }));
  };

  const toggleMetric = (
    channel: keyof typeof perms.analytics,
    metric: string,
  ) => {
    setPerms((prev) => ({
      ...prev,
      analytics: {
        ...prev.analytics,
        [channel]: {
          ...(prev.analytics as any)[channel],
          [metric]: !(prev.analytics as any)[channel][metric],
        },
      },
    }));
  };

  const handleSave = () => {
    onSave(perms, localPasscode, nickname);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6 shadow-lg">
        <h2 className="mb-4 text-xl font-semibold">Edit Client</h2>

        {/* Passcode + Nickname */}
        <div className="mb-4 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium">Passcode</label>
            <input
              type="text"
              maxLength={5}
              pattern="[0-9]{5}"
              value={localPasscode}
              onChange={(e) => setLocalPasscode(e.target.value)}
              className="w-full rounded-md border p-2"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Nickname</label>
            <input
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              className="w-full rounded-md border p-2"
            />
          </div>
        </div>

        {/* Navigation section */}
        <div className="space-y-2">
          <h3 className="text-lg font-medium">Navigation</h3>
          <div className="grid grid-cols-2 gap-2">
            {Object.keys(DEFAULT_PERMISSIONS.navigation).map((key) => (
              <label key={key} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4"
                  checked={perms.navigation[key as keyof typeof perms.navigation]}
                  onChange={() => toggleNav(key as keyof typeof perms.navigation)}
                />
                <span className="capitalize">{key.replace(/_/g, ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Analytics section */}
        <div className="mt-6 space-y-4">
          <h3 className="text-lg font-medium">Analytics Metrics</h3>
          {Object.entries(DEFAULT_PERMISSIONS.analytics).map(([channel, metrics]) => (
            <div key={channel} className="border-t pt-4 first:mt-0 first:border-0">
              <h4 className="mb-2 font-semibold capitalize">{channel}</h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.keys(metrics).map((metricKey) => (
                  <label key={metricKey} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      className="h-4 w-4"
                      checked={
                        (perms.analytics as any)[channel][metricKey]
                      }
                      onChange={() =>
                        toggleMetric(channel as any, metricKey as string)
                      }
                    />
                    <span className="capitalize">{metricKey.replace(/_/g, ' ')}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Action buttons */}
        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-md border px-4 py-2 text-sm hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
