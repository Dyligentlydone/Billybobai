const express = require('express');
const router = express.Router();
const twilio = require('twilio');
const winston = require('winston');
const { body, validationResult } = require('express-validator');

// Initialize Twilio client
const twilioClient = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

// SMS webhook endpoint
router.post('/sms', async (req, res) => {
  try {
    const twiml = new twilio.twiml.MessagingResponse();
    const incomingMessage = req.body.Body;
    const from = req.body.From;

    // Process incoming message and get workflow response
    const response = await processIncomingSMS(incomingMessage, from);
    twiml.message(response);

    res.type('text/xml').send(twiml.toString());
  } catch (error) {
    winston.error('Error processing SMS webhook:', error);
    res.status(500).send('Error processing SMS');
  }
});

// Voice webhook endpoint
router.post('/voice', async (req, res) => {
  try {
    const twiml = new twilio.twiml.VoiceResponse();
    const from = req.body.From;

    // Process incoming call and get workflow response
    const response = await processIncomingCall(from);
    
    if (response.type === 'gather') {
      const gather = twiml.gather({
        numDigits: response.numDigits,
        action: response.action
      });
      gather.say(response.message);
    } else {
      twiml.say(response.message);
    }

    res.type('text/xml').send(twiml.toString());
  } catch (error) {
    winston.error('Error processing voice webhook:', error);
    res.status(500).send('Error processing voice call');
  }
});

// Flex webhook endpoint
router.post('/flex', async (req, res) => {
  try {
    const event = req.body;
    await processFlexEvent(event);
    res.status(200).send('OK');
  } catch (error) {
    winston.error('Error processing Flex webhook:', error);
    res.status(500).send('Error processing Flex event');
  }
});

// Configure webhooks for a client
router.post('/config', [
  body('clientId').isString().notEmpty(),
  body('phoneNumber').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { clientId, phoneNumber } = req.body;
    const baseUrl = process.env.BASE_URL;

    // Update SMS webhook
    await twilioClient.incomingPhoneNumbers(phoneNumber)
      .update({
        smsUrl: `${baseUrl}/api/integrations/twilio/sms`,
        voiceUrl: `${baseUrl}/api/integrations/twilio/voice`
      });

    // Configure Flex webhook
    await twilioClient.flexApi.v1.flexFlows
      .create({
        channelType: 'web',
        integrationType: 'external',
        integration: {
          url: `${baseUrl}/api/integrations/twilio/flex`,
          workspaceSid: process.env.TWILIO_WORKSPACE_SID
        }
      });

    res.json({ message: 'Webhooks configured successfully' });
  } catch (error) {
    winston.error('Error configuring webhooks:', error);
    res.status(500).json({ error: 'Failed to configure webhooks' });
  }
});

// Send SMS
router.post('/send-sms', [
  body('to').isString().notEmpty(),
  body('message').isString().notEmpty(),
  body('clientId').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { to, message, clientId } = req.body;
    const result = await twilioClient.messages.create({
      to,
      body: message,
      from: process.env.TWILIO_PHONE_NUMBER
    });

    res.json(result);
  } catch (error) {
    winston.error('Error sending SMS:', error);
    res.status(500).json({ error: 'Failed to send SMS' });
  }
});

// Make voice call
router.post('/make-call', [
  body('to').isString().notEmpty(),
  body('twiml').isString().notEmpty(),
  body('clientId').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { to, twiml, clientId } = req.body;
    const result = await twilioClient.calls.create({
      to,
      from: process.env.TWILIO_PHONE_NUMBER,
      twiml
    });

    res.json(result);
  } catch (error) {
    winston.error('Error making call:', error);
    res.status(500).json({ error: 'Failed to make call' });
  }
});

// Helper functions
async function processIncomingSMS(message, from) {
  // Implement workflow logic here
  return 'Thank you for your message. We will process it shortly.';
}

async function processIncomingCall(from) {
  // Implement workflow logic here
  return {
    type: 'gather',
    numDigits: 1,
    action: '/api/integrations/twilio/voice-menu',
    message: 'Welcome to our service. Press 1 for sales, 2 for support.'
  };
}

async function processFlexEvent(event) {
  // Implement Flex event handling logic here
  winston.info('Processing Flex event:', event);
}

module.exports = router;
