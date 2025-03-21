const express = require('express');
const router = express.Router();
const sgMail = require('@sendgrid/mail');
const sgClient = require('@sendgrid/client');
const winston = require('winston');
const { body, validationResult } = require('express-validator');
const crypto = require('crypto');

// Initialize SendGrid
sgMail.setApiKey(process.env.SENDGRID_API_KEY);
sgClient.setApiKey(process.env.SENDGRID_API_KEY);

// Verify webhook signatures
function verifyWebhook(req, res, next) {
  try {
    const signature = req.get('X-Twilio-Email-Event-Webhook-Signature');
    const timestamp = req.get('X-Twilio-Email-Event-Webhook-Timestamp');
    const payload = JSON.stringify(req.body);

    const verifySignature = crypto
      .createHmac('sha256', process.env.SENDGRID_WEBHOOK_SECRET)
      .update(`${timestamp}${payload}`)
      .digest('hex');

    if (verifySignature === signature) {
      next();
    } else {
      res.status(401).json({ error: 'Invalid signature' });
    }
  } catch (error) {
    winston.error('Error verifying webhook:', error);
    res.status(401).json({ error: 'Invalid signature' });
  }
}

// Email webhook endpoint
router.post('/webhook', verifyWebhook, async (req, res) => {
  try {
    const events = req.body;
    await processEmailEvents(events);
    res.status(200).send('OK');
  } catch (error) {
    winston.error('Error processing email webhook:', error);
    res.status(500).send('Error processing webhook');
  }
});

// Send email
router.post('/send', [
  body('to').isEmail(),
  body('subject').isString().notEmpty(),
  body('templateId').isString().notEmpty(),
  body('dynamicTemplateData').isObject(),
  body('clientId').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { to, subject, templateId, dynamicTemplateData, clientId } = req.body;

    const msg = {
      to,
      from: process.env.SENDGRID_FROM_EMAIL,
      subject,
      templateId,
      dynamicTemplateData,
      trackingSettings: {
        clickTracking: { enable: true },
        openTracking: { enable: true }
      }
    };

    const result = await sgMail.send(msg);
    res.json(result);
  } catch (error) {
    winston.error('Error sending email:', error);
    res.status(500).json({ error: 'Failed to send email' });
  }
});

// Create dynamic template
router.post('/templates', [
  body('name').isString().notEmpty(),
  body('subject').isString().notEmpty(),
  body('html').isString().notEmpty(),
  body('clientId').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { name, subject, html, clientId } = req.body;

    // Create template
    const [templateResponse] = await sgClient.request({
      method: 'POST',
      url: '/v3/templates',
      body: {
        name,
        generation: 'dynamic'
      }
    });

    // Add template version
    const [versionResponse] = await sgClient.request({
      method: 'POST',
      url: `/v3/templates/${templateResponse.body.id}/versions`,
      body: {
        template_id: templateResponse.body.id,
        name,
        subject,
        html_content: html,
        active: 1
      }
    });

    res.json({
      templateId: templateResponse.body.id,
      versionId: versionResponse.body.id
    });
  } catch (error) {
    winston.error('Error creating template:', error);
    res.status(500).json({ error: 'Failed to create template' });
  }
});

// Get email statistics
router.get('/stats', [
  body('clientId').isString().notEmpty(),
  body('startDate').isString().notEmpty(),
  body('endDate').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { startDate, endDate } = req.query;

    const [response] = await sgClient.request({
      method: 'GET',
      url: '/v3/stats',
      qs: {
        start_date: startDate,
        end_date: endDate,
        aggregated_by: 'day'
      }
    });

    res.json(response.body);
  } catch (error) {
    winston.error('Error fetching email stats:', error);
    res.status(500).json({ error: 'Failed to fetch email stats' });
  }
});

// Helper functions
async function processEmailEvents(events) {
  for (const event of events) {
    try {
      winston.info('Processing email event:', {
        eventType: event.event,
        emailId: event.sg_message_id
      });

      // Implement workflow logic here based on event type
      switch (event.event) {
        case 'delivered':
          // Handle delivery
          break;
        case 'open':
          // Handle open
          break;
        case 'click':
          // Handle click
          break;
        case 'bounce':
          // Handle bounce
          break;
        default:
          winston.info('Unhandled email event type:', event.event);
      }
    } catch (error) {
      winston.error('Error processing email event:', error);
    }
  }
}

module.exports = router;
