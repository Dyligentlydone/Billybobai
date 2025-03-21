import { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import WorkflowBuilder from '../components/workflows/WorkflowBuilder';

interface Workflow {
  _id: string;
  name: string;
  status: 'active' | 'draft' | 'archived';
  createdAt: string;
  updatedAt: string;
}

export default function Workflows() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const { data: workflows, isLoading } = useQuery<Workflow[]>(
    'workflows',
    async () => {
      const { data } = await axios.get('/api/workflows');
      return data;
    }
  );

  if (isCreating || selectedWorkflow) {
    return (
      <div className="space-y-6">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">
              {isCreating ? 'Create Workflow' : 'Edit Workflow'}
            </h1>
            <p className="mt-2 text-sm text-gray-700">
              {isCreating
                ? 'Create a new workflow by adding and connecting nodes.'
                : 'Edit your existing workflow by modifying nodes and connections.'}
            </p>
          </div>
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
            <button
              type="button"
              onClick={() => {
                setSelectedWorkflow(null);
                setIsCreating(false);
              }}
              className="inline-flex items-center justify-center rounded-md border border-transparent bg-gray-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 sm:w-auto"
            >
              Back to Workflows
            </button>
          </div>
        </div>
        <WorkflowBuilder
          clientId="1"
          workflowId={selectedWorkflow || undefined}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Workflows</h1>
          <p className="mt-2 text-sm text-gray-700">
            Create and manage your communication workflows.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            onClick={() => setIsCreating(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
          >
            Create Workflow
          </button>
        </div>
      </div>

      <div className="mt-8 flex flex-col">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              {isLoading ? (
                <div className="p-4 text-center text-sm text-gray-700">
                  Loading workflows...
                </div>
              ) : !workflows?.length ? (
                <div className="p-4 text-center text-sm text-gray-700">
                  No workflows yet. Create your first one!
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6"
                      >
                        Name
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                      >
                        Status
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                      >
                        Created
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                      >
                        Last Updated
                      </th>
                      <th
                        scope="col"
                        className="relative py-3.5 pl-3 pr-4 sm:pr-6"
                      >
                        <span className="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {workflows.map((workflow) => (
                      <tr key={workflow._id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                          {workflow.name}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <span
                            className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                              workflow.status === 'active'
                                ? 'bg-green-100 text-green-800'
                                : workflow.status === 'draft'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {workflow.status}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {new Date(workflow.createdAt).toLocaleDateString()}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {new Date(workflow.updatedAt).toLocaleDateString()}
                        </td>
                        <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                          <button
                            onClick={() => setSelectedWorkflow(workflow._id)}
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            Edit
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
