import { useState } from 'react';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import BusinessSelector from '../components/business/BusinessSelector';

export default function Analytics() {
  const [selectedBusinessId, setSelectedBusinessId] = useState<string>('');

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
          <p className="mt-2 text-sm text-gray-700">
            View metrics and performance for your SMS automation workflows.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <BusinessSelector onBusinessChange={setSelectedBusinessId} />
        </div>
      </div>
      
      {selectedBusinessId ? (
        <AnalyticsDashboard clientId={selectedBusinessId} />
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">Select a business to view its analytics</p>
        </div>
      )}
    </div>
  );
}
