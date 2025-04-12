import { Handle, Position } from 'reactflow';

interface TwilioNodeProps {
  data: {
    label: string;
    type?: string;
    aiModel?: string;
    prompt?: string;
    phoneNumber?: string;
    messageTemplate?: string;
    webhookUrl?: string;
    onUpdate?: (data: any) => void;
  };
}

export default function TwilioNode({ data }: TwilioNodeProps) {
  return (
    <div className="bg-blue-100 p-4 rounded-lg shadow-md min-w-[300px]">
      <Handle type="target" position={Position.Left} />
      
      <div className="space-y-4">
        <h3 className="font-bold text-blue-800 text-lg">{data.label}</h3>
        
        <div className="space-y-2">
          <label className="block text-sm font-medium text-blue-700">Message Type</label>
          <select
            value={data.type || 'sms'}
            onChange={(e) => data.onUpdate?.({ ...data, type: e.target.value })}
            className="w-full p-2 border rounded bg-white"
          >
            <option value="sms">SMS</option>
            <option value="voice">Voice</option>
            <option value="flex">Flex</option>
            <option value="whatsapp">WhatsApp</option>
          </select>
        </div>

        {(data.type === 'sms' || data.type === 'whatsapp') && (
          <>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-blue-700">AI Model (Optional)</label>
              <select
                value={data.aiModel || ''}
                onChange={(e) => data.onUpdate?.({ ...data, aiModel: e.target.value })}
                className="w-full p-2 border rounded bg-white"
              >
                <option value="">No AI</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="claude-2">Claude 2</option>
              </select>
            </div>

            {data.aiModel && (
              <div className="space-y-2">
                <label className="block text-sm font-medium text-blue-700">System Prompt</label>
                <textarea
                  value={data.prompt || ''}
                  onChange={(e) => data.onUpdate?.({ ...data, prompt: e.target.value })}
                  placeholder="Enter the AI agent's system prompt..."
                  className="w-full p-2 border rounded bg-white h-24 resize-none"
                />
              </div>
            )}

            {!data.aiModel && (
              <div className="space-y-2">
                <label className="block text-sm font-medium text-blue-700">Message Template</label>
                <textarea
                  value={data.messageTemplate || ''}
                  onChange={(e) => data.onUpdate?.({ ...data, messageTemplate: e.target.value })}
                  placeholder="Enter message template with {{variables}}..."
                  className="w-full p-2 border rounded bg-white h-24 resize-none"
                />
              </div>
            )}
          </>
        )}

        {data.type === 'voice' && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-blue-700">Voice Message</label>
            <textarea
              value={data.messageTemplate || ''}
              onChange={(e) => data.onUpdate?.({ ...data, messageTemplate: e.target.value })}
              placeholder="Enter TwiML or voice message..."
              className="w-full p-2 border rounded bg-white h-24 resize-none"
            />
          </div>
        )}

        <div className="space-y-2">
          <label className="block text-sm font-medium text-blue-700">Twilio Phone Number</label>
          <input
            type="text"
            value={data.phoneNumber || ''}
            onChange={(e) => data.onUpdate?.({ ...data, phoneNumber: e.target.value })}
            placeholder="+1234567890"
            className="w-full p-2 border rounded bg-white"
          />
        </div>

        {data.webhookUrl && (
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <h4 className="text-sm font-medium text-blue-800 mb-2">Webhook Configuration</h4>
            <div className="text-xs text-blue-600 font-mono break-all">
              {data.webhookUrl}
            </div>
            <p className="text-xs text-blue-700 mt-2">
              Configure this URL in your Twilio dashboard for {data.type} webhooks
            </p>
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}
