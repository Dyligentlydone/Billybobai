import React from 'react';
import {
  Node,
  Edge,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  Connection,
  MarkerType,
  NodeChange,
  EdgeChange,
  Background,
  Controls,
  Panel,
  ReactFlow,
} from 'reactflow';
import { useQuery } from 'react-query';
import axios from 'axios';
import 'reactflow/dist/style.css';
import TwilioNode from './nodes/TwilioNode';
import SendGridNode from './nodes/SendGridNode';
import ZendeskNode from './nodes/ZendeskNode';
import ResponseNode from './nodes/ResponseNode';
import WorkflowExecution from './WorkflowExecution';

interface Workflow {
  id: string;
  name: string;
  status: 'draft' | 'active';
  nodes: WorkflowNode[];
  edges: Edge[];
}

interface WorkflowBuilderProps {
  clientId?: string;
  workflowId?: string;
  smsConfig?: any;
}

interface WorkflowData {
  label?: string;
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
  responseType?: 'success' | 'error' | 'timeout';
  action?: string;
  webhookUrl?: string;
  onUpdate?: (data: any) => void;
  position?: { x: number; y: number };
}

interface WorkflowNode extends Node {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: WorkflowData;
}

const nodeTypes = {
  twilio: TwilioNode,
  sendgrid: SendGridNode,
  zendesk: ZendeskNode,
  response: ResponseNode,
};

const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  workflowId
}) => {
  const [nodes, setNodes] = React.useState<WorkflowNode[]>([]);
  const [edges, setEdges] = React.useState<Edge[]>([]);
  const [showExecutions] = React.useState(false);

  const { data: workflow } = useQuery<Workflow>(
    ['workflow', workflowId],
    async () => {
      if (!workflowId) return null;
      const { data } = await axios.get(`/api/workflows/${workflowId}`);
      return data;
    },
    {
      enabled: !!workflowId,
      onSuccess: (data: Workflow | null) => {
        if (data) {
          setNodes(data.nodes);
          setEdges(data.edges);
        }
      }
    }
  );

  const handleNodeChange = React.useCallback((changes: NodeChange[]) => {
    setNodes((nds: WorkflowNode[]) => applyNodeChanges(changes, nds) as WorkflowNode[]);
  }, [setNodes]);

  const handleEdgeChange = React.useCallback((changes: EdgeChange[]) => {
    setEdges((eds: Edge[]) => applyEdgeChanges(changes, eds));
  }, [setEdges]);

  const onConnect = React.useCallback((params: Connection) => {
    setEdges((eds: Edge[]) => addEdge({ ...params, markerEnd: { type: MarkerType.ArrowClosed } }, eds));
  }, [setEdges]);

  React.useEffect(() => {
    if (workflow) {
      setNodes(workflow.nodes);
      setEdges(workflow.edges);
    }
  }, [workflow]);

  return (
    <div className="space-y-6">
      <div className="h-[calc(100vh-16rem)]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={handleNodeChange}
          onEdgesChange={handleEdgeChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
          <Panel position="top-right">
            <div className="flex space-x-2">
              {/* Add your panel content here */}
            </div>
          </Panel>
        </ReactFlow>
      </div>
      {showExecutions && workflowId && (
        <WorkflowExecution workflowId={workflowId} />
      )}
    </div>
  );
};

export default WorkflowBuilder;
