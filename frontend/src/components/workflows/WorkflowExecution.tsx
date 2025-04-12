import { useQuery } from 'react-query';
import { format } from 'date-fns';

interface ExecutionProps {
  workflowId: string;
  executionId?: string;
}

interface NodeExecution {
  node_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'retrying';
  start_time: string;
  end_time?: string;
  output?: any;
  error?: string;
  retry_count: number;
}

interface WorkflowExecution {
  workflow_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'retrying';
  start_time: string;
  end_time?: string;
  input_data: any;
  variables: any;
  node_executions: Record<string, NodeExecution>;
  error?: string;
}

export default function WorkflowExecution({ workflowId, executionId }: ExecutionProps) {
  // Fetch executions
  const { data: executions } = useQuery<Record<string, WorkflowExecution>>(
    ['workflow-executions', workflowId],
    async () => {
      const response = await fetch(`/api/workflows/${workflowId}/executions`);
      if (!response.ok) throw new Error('Failed to fetch executions');
      return response.json();
    },
    {
      enabled: !executionId
    }
  );

  // Fetch specific execution
  const { data: execution } = useQuery<WorkflowExecution>(
    ['workflow-execution', workflowId, executionId],
    async () => {
      const response = await fetch(`/api/workflows/${workflowId}/executions/${executionId}`);
      if (!response.ok) throw new Error('Failed to fetch execution');
      return response.json();
    },
    {
      enabled: !!executionId
    }
  );

  if (executionId && !execution) {
    return <div>Loading execution...</div>;
  }

  if (!executionId && !executions) {
    return <div>Loading executions...</div>;
  }

  if (executionId) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Execution Details</h2>
        <ExecutionDetails execution={execution!} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Workflow Executions</h2>
      <div className="space-y-4">
        {Object.entries(executions!).map(([id, execution]) => (
          <div key={id} className="border rounded-lg p-4 hover:bg-gray-50">
            <h3 className="text-lg font-semibold">
              Execution {format(new Date(execution.start_time), 'PPpp')}
            </h3>
            <ExecutionDetails execution={execution} />
          </div>
        ))}
      </div>
    </div>
  );
}

function ExecutionDetails({ execution }: { execution: WorkflowExecution }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="font-medium text-gray-500">Status</h4>
          <StatusBadge status={execution.status} />
        </div>
        <div>
          <h4 className="font-medium text-gray-500">Duration</h4>
          <p>
            {execution.end_time
              ? `${Math.round(
                  (new Date(execution.end_time).getTime() -
                    new Date(execution.start_time).getTime()) /
                    1000
                )} seconds`
              : 'Running...'}
          </p>
        </div>
      </div>

      <div>
        <h4 className="font-medium text-gray-500 mb-2">Input Data</h4>
        <pre className="bg-gray-50 p-3 rounded text-sm">
          {JSON.stringify(execution.input_data, null, 2)}
        </pre>
      </div>

      <div>
        <h4 className="font-medium text-gray-500 mb-2">Node Executions</h4>
        <div className="space-y-3">
          {Object.entries(execution.node_executions).map(([nodeId, nodeExec]) => (
            <div key={nodeId} className="border rounded p-3">
              <div className="flex items-center justify-between mb-2">
                <h5 className="font-medium">{nodeId}</h5>
                <StatusBadge status={nodeExec.status} />
              </div>
              {nodeExec.error && (
                <div className="text-red-600 text-sm mt-2">{nodeExec.error}</div>
              )}
              {nodeExec.output && (
                <pre className="bg-gray-50 p-2 rounded text-sm mt-2">
                  {JSON.stringify(nodeExec.output, null, 2)}
                </pre>
              )}
            </div>
          ))}
        </div>
      </div>

      {execution.error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Workflow Execution Error
              </h3>
              <div className="mt-2 text-sm text-red-700">{execution.error}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    retrying: 'bg-purple-100 text-purple-800'
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        colors[status as keyof typeof colors]
      }`}
    >
      {status}
    </span>
  );
}
