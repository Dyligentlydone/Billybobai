const mongoose = require('mongoose');

const workflowSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  client: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Client',
    required: true
  },
  description: String,
  naturalLanguageInput: {
    type: String,
    required: true
  },
  channels: [{
    type: String,
    enum: ['email', 'sms', 'voice', 'whatsapp', 'webchat'],
    required: true
  }],
  configuration: {
    email: {
      templates: [{
        name: String,
        subject: String,
        content: String,
        triggers: [String]
      }]
    },
    sms: {
      templates: [{
        name: String,
        content: String,
        triggers: [String]
      }]
    },
    voice: {
      ivrFlow: Object,
      scripts: [{
        name: String,
        content: String,
        triggers: [String]
      }]
    },
    webchat: {
      botConfig: Object,
      flowConfig: Object
    }
  },
  zendeskIntegration: {
    enabled: Boolean,
    triggerConditions: [String],
    ticketPriority: String,
    ticketTags: [String]
  },
  status: {
    type: String,
    enum: ['draft', 'active', 'paused', 'archived'],
    default: 'draft'
  },
  metrics: {
    messagesSent: { type: Number, default: 0 },
    callsHandled: { type: Number, default: 0 },
    ticketsCreated: { type: Number, default: 0 },
    estimatedMonthlyCost: Number
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

workflowSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Workflow', workflowSchema);
