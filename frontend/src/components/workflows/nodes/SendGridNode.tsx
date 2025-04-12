import { Handle, Position } from 'reactflow';

interface SendGridNodeProps {
  data: {
    label: string;
    templateId?: string;
    emailType?: string;
    subject?: string;
    content?: string;
    webhookUrl?: string;
    onUpdate?: (data: any) => void;
  };
}

export default function SendGridNode({ data }: SendGridNodeProps) {
  return (
    <div className="bg-green-100 p-4 rounded-lg shadow-md min-w-[300px]">
      <Handle type="target" position={Position.Left} />
      
      <div className="space-y-4">
        <h3 className="font-bold text-green-800 text-lg">{data.label}</h3>
        
        <div className="space-y-2">
          <label className="block text-sm font-medium text-green-700">Email Type</label>
          <select
            value={data.emailType || 'template'}
            onChange={(e) => data.onUpdate?.({ ...data, emailType: e.target.value })}
            className="w-full p-2 border rounded bg-white"
          >
            <option value="template">Template</option>
            <option value="custom">Custom</option>
            <option value="dynamic">Dynamic</option>
          </select>
        </div>

        {data.emailType === 'template' && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-green-700">Template ID</label>
            <input
              type="text"
              value={data.templateId || ''}
              onChange={(e) => data.onUpdate?.({ ...data, templateId: e.target.value })}
              placeholder="d-abc123..."
              className="w-full p-2 border rounded bg-white"
            />
          </div>
        )}

        {data.emailType === 'custom' && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-green-700">Email Content</label>
            <textarea
              value={data.content || ''}
              onChange={(e) => data.onUpdate?.({ ...data, content: e.target.value })}
              placeholder="Enter HTML content..."
              className="w-full p-2 border rounded bg-white h-24 resize-none font-mono"
            />
          </div>
        )}

        <div className="space-y-2">
          <label className="block text-sm font-medium text-green-700">Subject</label>
          <input
            type="text"
            value={data.subject || ''}
            onChange={(e) => data.onUpdate?.({ ...data, subject: e.target.value })}
            placeholder="Email subject..."
            className="w-full p-2 border rounded bg-white"
          />
        </div>

        {data.webhookUrl && (
          <div className="mt-4 p-3 bg-green-50 rounded-md">
            <h4 className="text-sm font-medium text-green-800 mb-2">Webhook Configuration</h4>
            <div className="text-xs text-green-600 font-mono break-all">
              {data.webhookUrl}
            </div>
            <p className="text-xs text-green-700 mt-2">
              Configure this URL in your SendGrid dashboard for Event Webhooks
            </p>
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}
