import { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

interface EmailConfigWizardProps {
  onComplete: (config: any) => void;
  onCancel: () => void;
}

interface EmailConfig {
  integration: {
    sendgridApiKey: string;
    fromEmail: string;
    fromName: string;
  };
  brandTone: {
    voiceType: string;
    greetings: string[];
    wordsToAvoid: string[];
  };
  templates: {
    businessHours: {
      enabled: boolean;
      timezone: string;
      hours: {
        [key: string]: {
          start: string;
          end: string;
        };
      };
    };
    outOfOffice: string;
  };
}

export default function EmailConfigWizard({
  onComplete,
  onCancel,
}: EmailConfigWizardProps) {
  const [step, setStep] = useState(1);
  const { register, handleSubmit, watch, formState: { errors } } = useForm<EmailConfig>();

  const onSubmit = (data: EmailConfig) => {
    // Format the data and pass it to parent
    onComplete({
      ...data,
      brandTone: {
        ...data.brandTone,
        greetings: data.brandTone.greetings[0].split(',').map(g => g.trim()),
        wordsToAvoid: data.brandTone.wordsToAvoid[0].split(',').map(w => w.trim())
      }
    });
  };

  return (
    <div className="space-y-8 divide-y divide-gray-200">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                SendGrid Integration
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure your SendGrid email settings.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-4">
                <label htmlFor="sendgridApiKey" className="block text-sm font-medium text-gray-700">
                  SendGrid API Key
                </label>
                <div className="mt-1">
                  <input
                    type="password"
                    {...register('integration.sendgridApiKey', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.sendgridApiKey && (
                    <p className="mt-2 text-sm text-red-600">API key is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="fromEmail" className="block text-sm font-medium text-gray-700">
                  From Email
                </label>
                <div className="mt-1">
                  <input
                    type="email"
                    {...register('integration.fromEmail', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.fromEmail && (
                    <p className="mt-2 text-sm text-red-600">From email is required</p>
                  )}
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="fromName" className="block text-sm font-medium text-gray-700">
                  From Name
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('integration.fromName', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  {errors.integration?.fromName && (
                    <p className="mt-2 text-sm text-red-600">From name is required</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Brand Voice Configuration
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Define how your automated emails should sound.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-3">
                <label htmlFor="voiceType" className="block text-sm font-medium text-gray-700">
                  Voice Type
                </label>
                <div className="mt-1">
                  <select
                    {...register('brandTone.voiceType', { required: true })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="formal">Formal</option>
                  </select>
                </div>
              </div>

              <div className="sm:col-span-6">
                <label htmlFor="greetings" className="block text-sm font-medium text-gray-700">
                  Greetings (comma-separated)
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('brandTone.greetings', { required: true })}
                    placeholder="Hi, Hello, Good morning"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
              </div>

              <div className="sm:col-span-6">
                <label htmlFor="wordsToAvoid" className="block text-sm font-medium text-gray-700">
                  Words to Avoid (comma-separated)
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    {...register('brandTone.wordsToAvoid', { required: true })}
                    placeholder="yeah, nah, cool"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Business Hours & Templates
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure when and how to respond to emails.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    {...register('templates.businessHours.enabled')}
                    className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <label htmlFor="businessHoursEnabled" className="ml-2 block text-sm text-gray-700">
                    Enable Business Hours
                  </label>
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="timezone" className="block text-sm font-medium text-gray-700">
                  Timezone
                </label>
                <div className="mt-1">
                  <select
                    {...register('templates.businessHours.timezone')}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                  </select>
                </div>
              </div>

              <div className="sm:col-span-6">
                <label htmlFor="outOfOffice" className="block text-sm font-medium text-gray-700">
                  Out of Office Message
                </label>
                <div className="mt-1">
                  <textarea
                    {...register('templates.outOfOffice')}
                    rows={3}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    placeholder="Thank you for your email. Our office is currently closed..."
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="pt-5">
          <div className="flex justify-end space-x-3">
            {step > 1 && (
              <button
                type="button"
                onClick={() => setStep(step - 1)}
                className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Previous
              </button>
            )}
            <button
              type="button"
              onClick={onCancel}
              className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Cancel
            </button>
            {step < 3 ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Create
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
