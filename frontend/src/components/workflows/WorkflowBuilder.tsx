import { useCallback, useState } from 'react';
import ReactFlow, {
  Connection,
  Edge,
  MarkerType,
  Panel,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import TwilioNode from './nodes/TwilioNode';
import SendGridNode from './nodes/SendGridNode';
import ZendeskNode from './nodes/ZendeskNode';
import ResponseNode from './nodes/ResponseNode';
import WorkflowExecution from './WorkflowExecution';
import { analyzeRequirements, getWebhookUrls, WorkflowConfig } from '../../services/api';
import axios from 'axios';

interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    type?: string;
    aiModel?: string;
    prompt?: string;
    phoneNumber?: string;
    messageTemplate?: string;
    emailType?: string;
    templateId?: string;
    subject?: string;
    priority?: string;
    category?: string;
    assignee?: string;
    responseType?: 'success' | 'error' | 'timeout';
    action?: string;
    webhookUrl?: string;
    onUpdate?: (data: any) => void;
  };
}

interface WorkflowBuilderProps {
  clientId: string;
  workflowId?: string;
}

interface Workflow {
  _id: string;
  name: string;
  status: 'active' | 'draft' | 'archived';
  nodes: WorkflowNode[];
  edges: Edge[];
  createdAt: string;
  updatedAt: string;
}

const nodeTypes = {
  twilio: TwilioNode,
  sendgrid: SendGridNode,
  zendesk: ZendeskNode,
  response: ResponseNode
};

const defaultPrompt = `You are a helpful AI assistant communicating via SMS. Your role is to:
1. Understand user requests and provide clear, concise responses
2. Maintain a friendly and professional tone
3. Ask clarifying questions when needed
4. Keep responses under 160 characters when possible
5. Escalate to a human agent when necessary`;

export default function WorkflowBuilder({ clientId, workflowId }: WorkflowBuilderProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNode[]>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [workflowName, setWorkflowName] = useState('New Workflow');
  const [aiDescription, setAiDescription] = useState('');
  const [showExecutions, setShowExecutions] = useState(false);
  const [executionInput, setExecutionInput] = useState('{}');
  const queryClient = useQueryClient();
  const webhookUrls = getWebhookUrls();

  // Fetch existing workflow
  const { data: workflow, isLoading } = useQuery<Workflow>(
    ['workflow', workflowId],
    async () => {
      if (!workflowId) return null;
      const { data } = await axios.get(`/api/workflows/${workflowId}`);
      return data;
    },
    {
      enabled: !!workflowId,
      onSuccess: (data) => {
        if (data) {
          setNodes(data.nodes);
          setEdges(data.edges);
          setWorkflowName(data.name);
        }
      }
    }
  );

  // AI workflow generation
  const aiMutation = useMutation(
    async (description: string) => {
      return await analyzeRequirements(description);
    },
    {
      onSuccess: (config: WorkflowConfig) => {
        const newNodes: WorkflowNode[] = [];
        let yPosition = 100;

        // Create nodes based on AI configuration
        if (config.twilio) {
          newNodes.push({
            id: `twilio-${Date.now()}`,
            type: 'twilio',
            position: { x: 100, y: yPosition },
            data: {
              label: 'Twilio Communication',
              type: config.twilio.type || 'sms',
              aiModel: config.twilio.aiEnabled === 'true' ? 'gpt-4' : undefined,
              prompt: defaultPrompt,
              webhookUrl: webhookUrls.twilio,
              onUpdate: createNodeUpdateHandler(`twilio-${Date.now()}`)
            }
          });
          yPosition += 150;
        }

        if (config.sendgrid) {
          newNodes.push({
            id: `sendgrid-${Date.now()}`,
            type: 'sendgrid',
            position: { x: 100, y: yPosition },
            data: {
              label: 'SendGrid Email',
              emailType: config.sendgrid.type || 'template',
              webhookUrl: webhookUrls.sendgrid,
              onUpdate: createNodeUpdateHandler(`sendgrid-${Date.now()}`)
            }
          });
          yPosition += 150;
        }

        if (config.zendesk) {
          newNodes.push({
            id: `zendesk-${Date.now()}`,
            type: 'zendesk',
            position: { x: 100, y: yPosition },
            data: {
              label: 'Zendesk Ticket',
              priority: 'normal',
              category: 'support',
              webhookUrl: webhookUrls.zendesk,
              onUpdate: createNodeUpdateHandler(`zendesk-${Date.now()}`)
            }
          });
          yPosition += 150;
        }

        // Add response handlers
        newNodes.push({
          id: `response-success-${Date.now()}`,
          type: 'response',
          position: { x: 400, y: 100 },
          data: {
            label: 'Success Handler',
            responseType: 'success',
            action: 'continue',
            onUpdate: createNodeUpdateHandler(`response-success-${Date.now()}`)
          }
        });

        newNodes.push({
          id: `response-error-${Date.now()}`,
          type: 'response',
          position: { x: 400, y: 250 },
          data: {
            label: 'Error Handler',
            responseType: 'error',
            action: 'retry',
            onUpdate: createNodeUpdateHandler(`response-error-${Date.now()}`)
          }
        });

        // Set nodes and show instructions
        setNodes(newNodes);
        toast.success('Workflow generated! Check setup instructions below.');
        
        // Show setup instructions
        if (config.instructions.length > 0) {
          const instructionsHtml = config.instructions
            .map(instruction => `• ${instruction}`)
            .join('\n');
          toast(instructionsHtml, { duration: 10000 });
        }
      },
      onError: (error) => {
        toast.error('Failed to generate workflow: ' + error.message);
      }
    }
  );

  const createNodeUpdateHandler = (nodeId: string) => (newData: any) => {
    setNodes((nds) =>
      nds.map((n) => {
        if (n.id === nodeId) {
          return { ...n, data: { ...newData, onUpdate: n.data.onUpdate } };
        }
        return n;
      })
    );
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, markerEnd: { type: MarkerType.ArrowClosed } }, eds)),
    [setEdges]
  );

  const saveMutation = useMutation(
    async (workflow: Partial<Workflow>) => {
      if (workflowId) {
        await axios.put(`/api/workflows/${workflowId}`, { ...workflow, clientId });
      } else {
        await axios.post('/api/workflows', { ...workflow, clientId });
      }
    },
    {
      onSuccess: () => {
        toast.success('Workflow saved successfully');
        queryClient.invalidateQueries('workflows');
      },
      onError: () => {
        toast.error('Failed to save workflow');
      }
    }
  );

  const handleSave = useCallback(() => {
    const cleanNodes = nodes.map(node => ({
      ...node,
      data: {
        ...node.data,
        onUpdate: undefined
      }
    }));

    saveMutation.mutate({
      name: workflowName,
      status: 'draft',
      nodes: cleanNodes,
      edges
    });
  }, [nodes, edges, workflowName, saveMutation]);

  const onAddNode = useCallback(
    (type: string) => {
      const newNode: WorkflowNode = {
        id: `${type}-${Date.now()}`,
        type,
        position: { x: 100, y: 100 },
        data: {
          ...getDefaultData(type)
        }
      };

      // Add onUpdate handler
      newNode.data.onUpdate = (newData: any) => {
        setNodes((nds) =>
          nds.map((n) => {
            if (n.id === newNode.id) {
              return { ...n, data: { ...newData, onUpdate: n.data.onUpdate } };
            }
            return n;
          })
        );
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [setNodes]
  );

  const getDefaultData = (type: string) => {
    switch (type) {
      case 'twilio':
        return {
          label: 'Twilio Communication',
          type: 'sms'
        };
      case 'sendgrid':
        return {
          label: 'SendGrid Email',
          emailType: 'template'
        };
      case 'zendesk':
        return {
          label: 'Zendesk Ticket',
          priority: 'normal',
          category: 'support'
        };
      case 'response':
        return {
          label: 'Response Handler',
          responseType: 'success',
          action: 'continue'
        };
      default:
        return { label: 'New Node' };
    }
  };

  // Execute workflow mutation
  const executeMutation = useMutation(
    async (input: any) => {
      const response = await fetch(`/api/workflows/${workflowId}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(input)
      });
      if (!response.ok) throw new Error('Failed to execute workflow');
      return response.json();
    },
    {
      onSuccess: () => {
        toast.success('Workflow execution started');
        setShowExecutions(true);
      },
      onError: (error) => {
        toast.error('Failed to execute workflow: ' + error.message);
      }
    }
  );

  return (
    <div className="space-y-6">
      <div className="h-[calc(100vh-16rem)]">
        <div className="mb-4 space-y-4">
          <div className="flex items-center justify-between">
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              className="text-xl font-semibold px-2 py-1 border rounded"
              placeholder="Workflow Name"
            />
            <div className="space-x-2">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                Save
              </button>
              {workflowId && workflow?.status === 'draft' && (
                <button
                  onClick={() => saveMutation.mutate()}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Activate
                </button>
              )}
            </div>
          </div>

          <div className="flex gap-4">
            <input
              type="text"
              value={aiDescription}
              onChange={(e) => setAiDescription(e.target.value)}
              placeholder="Describe your workflow (e.g., 'Create a customer support system with email and chat')"
              className="flex-1 px-4 py-2 border rounded"
            />
            <button
              onClick={() => aiMutation.mutate(aiDescription)}
              disabled={!aiDescription}
              className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
            >
              Generate Workflow
            </button>
          </div>
        </div>

        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Quick Guide
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>1. Name your workflow and describe it for AI generation</p>
                <p>2. Add communication nodes (Twilio, SendGrid, Zendesk)</p>
                <p>3. Configure each node's settings and webhooks</p>
                <p>4. Add Response Handlers to manage outcomes</p>
                <p>5. Connect nodes to create the workflow</p>
                <p>6. Save and activate your workflow</p>
              </div>
            </div>
          </div>
        </div>
        
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
          <Panel position="top-right">
            <div className="space-x-2">
              <button
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                onClick={() => onAddNode('twilio')}
              >
                Add Twilio Node
              </button>
              <button
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                onClick={() => onAddNode('sendgrid')}
              >
                Add SendGrid Node
              </button>
              <button
                className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
                onClick={() => onAddNode('zendesk')}
              >
                Add Zendesk Node
              </button>
              <button
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                onClick={() => onAddNode('response')}
              >
                Add Response Handler
              </button>
            </div>
          </Panel>
        </ReactFlow>
      </div>

      {workflowId && workflow?.status === 'active' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium mb-4">Execute Workflow</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Input Data (JSON)
              </label>
              <textarea
                value={executionInput}
                onChange={(e) => setExecutionInput(e.target.value)}
                className="w-full h-32 p-2 border rounded font-mono text-sm"
                placeholder="{}"
              />
            </div>
            <div className="flex justify-between items-center">
              <button
                onClick={() => {
                  try {
                    const input = JSON.parse(executionInput);
                    executeMutation.mutate(input);
                  } catch (e) {
                    toast.error('Invalid JSON input');
                  }
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                Execute Workflow
              </button>
              <button
                onClick={() => setShowExecutions((show) => !show)}
                className="px-4 py-2 text-indigo-600 hover:text-indigo-800"
              >
                {showExecutions ? 'Hide Executions' : 'Show Executions'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showExecutions && workflowId && (
        <div className="bg-white shadow rounded-lg p-6">
          <WorkflowExecution workflowId={workflowId} />
        </div>
      )}
    </div>
  );
}
