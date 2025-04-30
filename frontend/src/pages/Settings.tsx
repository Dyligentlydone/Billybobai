import { useState } from 'react';
import { Tab } from '@headlessui/react';
import ClientAccounts from '../components/settings/ClientAccounts';
import { useBusiness } from '../contexts/BusinessContext';

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function Settings() {
  const { isAdmin } = useBusiness();
  const [selectedTab, setSelectedTab] = useState(0);

  const tabs = [
    ...(isAdmin ? [{ name: 'Client Accounts', content: <ClientAccounts /> }] : []),
    { name: 'General', content: 'General settings coming soon...' },
    { name: 'Notifications', content: 'Notification settings coming soon...' },
  ];

  return (
    <div className="w-full space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
          <p className="mt-2 text-sm text-gray-700">
            Configure your application settings and preferences.
          </p>
        </div>
      </div>

      <div className="w-full px-2 sm:px-0">
        <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
          <Tab.List className="flex space-x-1 rounded-xl bg-gray-100 p-1">
            {tabs.map((tab) => (
              <Tab
                key={tab.name}
                className={({ selected }) =>
                  classNames(
                    'w-full rounded-lg py-2.5 text-sm font-medium leading-5',
                    selected
                      ? 'bg-white text-gray-900 shadow'
                      : 'text-gray-500 hover:text-gray-700'
                  )
                }
              >
                {tab.name}
              </Tab>
            ))}
          </Tab.List>
          <Tab.Panels className="mt-6">
            {tabs.map((tab, idx) => (
              <Tab.Panel key={idx} className="p-3">
                {tab.content}
              </Tab.Panel>
            ))}
          </Tab.Panels>
        </Tab.Group>
      </div>
    </div>
  );
}
