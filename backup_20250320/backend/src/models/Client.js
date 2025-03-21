const mongoose = require('mongoose');
const encrypt = require('mongoose-encryption');

const clientSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  twilioConfig: {
    accountSid: String,
    authToken: String,
    phoneNumber: String
  },
  sendgridConfig: {
    apiKey: String,
    senderEmail: String
  },
  zendeskConfig: {
    subdomain: String,
    email: String,
    apiToken: String
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

// Encrypt sensitive fields
const encKey = process.env.ENCRYPTION_KEY;
clientSchema.plugin(encrypt, {
  encryptionKey: encKey,
  signingKey: encKey,
  encryptedFields: ['twilioConfig.authToken', 'sendgridConfig.apiKey', 'zendeskConfig.apiToken']
});

module.exports = mongoose.model('Client', clientSchema);
