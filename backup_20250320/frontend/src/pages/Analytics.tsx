import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';

export default function Analytics() {
  // TODO: Get clientId from context or URL params
  const clientId = '1'; // Temporary hardcoded value

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
          <p className="mt-2 text-sm text-gray-700">
            View metrics and trends across your Twilio, SendGrid, and Zendesk integrations.
          </p>
        </div>
      </div>
      <AnalyticsDashboard clientId={clientId} />
    </div>
  );
}
