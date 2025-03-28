import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircleIcon } from '@heroicons/react/24/solid';

interface Props {
  businessName: string;
  businessId: string;
  phoneNumber: string;
}

const SuccessScreen: React.FC<Props> = ({ businessName, businessId, phoneNumber }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <CheckCircleIcon className="mx-auto h-16 w-16 text-green-500" />
          <h2 className="mt-6 text-3xl font-bold text-gray-900">Setup Complete!</h2>
          <p className="mt-2 text-sm text-gray-500">
            Your SMS automation is ready to go
          </p>
        </div>

        <div className="mt-8 space-y-6">
          <div className="rounded-md bg-gray-50 p-4">
            <dl className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Business Name</dt>
                <dd className="mt-1 text-lg font-semibold text-gray-900">{businessName}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Business ID</dt>
                <dd className="mt-1 text-lg font-mono text-gray-900">{businessId}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Phone Number</dt>
                <dd className="mt-1 text-lg font-semibold text-gray-900">{phoneNumber}</dd>
              </div>
            </dl>
          </div>

          <div className="flex flex-col space-y-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Go to Dashboard
            </button>
            
            <button
              onClick={() => navigate('/settings')}
              className="w-full flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Configure Settings
            </button>
          </div>

          <div className="text-center">
            <p className="text-xs text-gray-500">
              Save your Business ID for future reference. You'll need it for API integrations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuccessScreen;
