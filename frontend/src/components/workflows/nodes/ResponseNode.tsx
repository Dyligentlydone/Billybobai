import { Handle, Position } from 'reactflow';

interface ResponseNodeProps {
  data: {
    label: string;
    responseType?: 'success' | 'error' | 'timeout';
    action?: string;
    onUpdate?: (data: any) => void;
  };
}

export default function ResponseNode({ data }: ResponseNodeProps) {
  return (
    <div className="bg-gray-100 p-4 rounded-lg shadow-md min-w-[250px]">
      <Handle type="target" position={Position.Left} />
      
      <div className="space-y-4">
        <h3 className="font-bold text-gray-800 text-lg">{data.label}</h3>
        
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Response Type</label>
          <select
            value={data.responseType || 'success'}
            onChange={(e) => data.onUpdate?.({ ...data, responseType: e.target.value })}
            className="w-full p-2 border rounded bg-white"
          >
            <option value="success">Success</option>
            <option value="error">Error</option>
            <option value="timeout">Timeout</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Action</label>
          <select
            value={data.action || 'continue'}
            onChange={(e) => data.onUpdate?.({ ...data, action: e.target.value })}
            className="w-full p-2 border rounded bg-white"
          >
            <option value="continue">Continue Conversation</option>
            <option value="end">End Conversation</option>
            <option value="transfer">Transfer to Human</option>
            <option value="retry">Retry Request</option>
          </select>
        </div>
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}
