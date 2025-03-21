import React from 'react';
import { Handle, Position } from 'reactflow';

interface ZendeskNodeProps {
  data: {
    label: string;
    priority?: string;
    category?: string;
    assignee?: string;
    webhookUrl?: string;
    customFields?: Record<string, any>;
    onUpdate?: (data: any) => void;
  };
}

export default function ZendeskNode({ data }: ZendeskNodeProps) {
  return (
    <div className="bg-purple-100 p-4 rounded-lg shadow-md min-w-[300px]">
      <Handle type="target" position={Position.Left} />
      
      <div className="space-y-4">
        <h3 className="font-bold text-purple-800 text-lg">{data.label}</h3>
        
        <div className="space-y-2">
          <label className="block text-sm font-medium text-purple-700">Priority</label>
          <select
            value={data.priority || 'normal'}
            onChange={(e) => data.onUpdate?.({ ...data, priority: e.target.value })}
            className="w-full p-2 border rounded bg-white"
          >
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-purple-700">Category</label>
          <select
            value={data.category || 'support'}
            onChange={(e) => data.onUpdate?.({ ...data, category: e.target.value })}
            className="w-full p-2 border rounded bg-white"
          >
            <option value="support">Support</option>
            <option value="billing">Billing</option>
            <option value="technical">Technical</option>
            <option value="feature">Feature Request</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-purple-700">Assignee Email</label>
          <input
            type="email"
            value={data.assignee || ''}
            onChange={(e) => data.onUpdate?.({ ...data, assignee: e.target.value })}
            placeholder="agent@company.com"
            className="w-full p-2 border rounded bg-white"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-purple-700">Custom Fields</label>
          <div className="bg-white rounded border p-2">
            <button
              onClick={() => {
                const fields = { ...(data.customFields || {}) };
                const key = `field_${Object.keys(fields).length + 1}`;
                fields[key] = '';
                data.onUpdate?.({ ...data, customFields: fields });
              }}
              className="w-full px-3 py-1 text-sm bg-purple-50 text-purple-700 rounded hover:bg-purple-100"
            >
              + Add Custom Field
            </button>
            {data.customFields && Object.entries(data.customFields).map(([key, value]) => (
              <div key={key} className="flex gap-2 mt-2">
                <input
                  type="text"
                  value={key}
                  onChange={(e) => {
                    const fields = { ...(data.customFields || {}) };
                    const oldValue = fields[key];
                    delete fields[key];
                    fields[e.target.value] = oldValue;
                    data.onUpdate?.({ ...data, customFields: fields });
                  }}
                  placeholder="Field name"
                  className="flex-1 p-1 text-sm border rounded"
                />
                <input
                  type="text"
                  value={value}
                  onChange={(e) => {
                    const fields = { ...(data.customFields || {}) };
                    fields[key] = e.target.value;
                    data.onUpdate?.({ ...data, customFields: fields });
                  }}
                  placeholder="Value"
                  className="flex-1 p-1 text-sm border rounded"
                />
                <button
                  onClick={() => {
                    const fields = { ...(data.customFields || {}) };
                    delete fields[key];
                    data.onUpdate?.({ ...data, customFields: fields });
                  }}
                  className="px-2 text-sm text-red-600 hover:text-red-800"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {data.webhookUrl && (
          <div className="mt-4 p-3 bg-purple-50 rounded-md">
            <h4 className="text-sm font-medium text-purple-800 mb-2">Webhook Configuration</h4>
            <div className="text-xs text-purple-600 font-mono break-all">
              {data.webhookUrl}
            </div>
            <p className="text-xs text-purple-700 mt-2">
              Configure this URL in your Zendesk admin settings for ticket webhooks
            </p>
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}
