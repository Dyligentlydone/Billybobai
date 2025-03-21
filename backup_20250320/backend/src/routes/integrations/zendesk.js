const express = require('express');
const router = express.Router();
const zendesk = require('node-zendesk');
const winston = require('winston');
const { body, validationResult } = require('express-validator');

// Initialize Zendesk client
function getZendeskClient(subdomain, email, token) {
  return zendesk.createClient({
    username: email,
    token: token,
    remoteUri: `https://${subdomain}.zendesk.com/api/v2`
  });
}

// Create ticket
router.post('/tickets', [
  body('subject').isString().notEmpty(),
  body('description').isString().notEmpty(),
  body('priority').isString().isIn(['low', 'normal', 'high', 'urgent']),
  body('type').isString().isIn(['question', 'incident', 'problem', 'task']),
  body('clientId').isString().notEmpty(),
  body('tags').isArray(),
  body('customFields').isObject().optional(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const {
      subject,
      description,
      priority,
      type,
      clientId,
      tags,
      customFields
    } = req.body;

    // Get client's Zendesk configuration
    const client = await getClientConfig(clientId);
    const zendeskClient = getZendeskClient(
      client.zendeskConfig.subdomain,
      client.zendeskConfig.email,
      client.zendeskConfig.apiToken
    );

    const ticket = {
      ticket: {
        subject,
        comment: { body: description },
        priority,
        type,
        tags,
        custom_fields: customFields
      }
    };

    const result = await new Promise((resolve, reject) => {
      zendeskClient.tickets.create(ticket, (err, req, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);
        }
      });
    });

    res.json(result);
  } catch (error) {
    winston.error('Error creating ticket:', error);
    res.status(500).json({ error: 'Failed to create ticket' });
  }
});

// Update ticket
router.put('/tickets/:id', [
  body('status').isString().isIn(['new', 'open', 'pending', 'hold', 'solved', 'closed']).optional(),
  body('priority').isString().isIn(['low', 'normal', 'high', 'urgent']).optional(),
  body('comment').isString().optional(),
  body('clientId').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { id } = req.params;
    const { status, priority, comment, clientId } = req.body;

    // Get client's Zendesk configuration
    const client = await getClientConfig(clientId);
    const zendeskClient = getZendeskClient(
      client.zendeskConfig.subdomain,
      client.zendeskConfig.email,
      client.zendeskConfig.apiToken
    );

    const ticket = {
      ticket: {
        status,
        priority
      }
    };

    if (comment) {
      ticket.ticket.comment = { body: comment };
    }

    const result = await new Promise((resolve, reject) => {
      zendeskClient.tickets.update(id, ticket, (err, req, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);
        }
      });
    });

    res.json(result);
  } catch (error) {
    winston.error('Error updating ticket:', error);
    res.status(500).json({ error: 'Failed to update ticket' });
  }
});

// Get ticket
router.get('/tickets/:id', [
  body('clientId').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { id } = req.params;
    const { clientId } = req.body;

    // Get client's Zendesk configuration
    const client = await getClientConfig(clientId);
    const zendeskClient = getZendeskClient(
      client.zendeskConfig.subdomain,
      client.zendeskConfig.email,
      client.zendeskConfig.apiToken
    );

    const result = await new Promise((resolve, reject) => {
      zendeskClient.tickets.show(id, (err, req, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);
        }
      });
    });

    res.json(result);
  } catch (error) {
    winston.error('Error fetching ticket:', error);
    res.status(500).json({ error: 'Failed to fetch ticket' });
  }
});

// Search tickets
router.get('/search', [
  body('query').isString().notEmpty(),
  body('clientId').isString().notEmpty(),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { query, clientId } = req.query;

    // Get client's Zendesk configuration
    const client = await getClientConfig(clientId);
    const zendeskClient = getZendeskClient(
      client.zendeskConfig.subdomain,
      client.zendeskConfig.email,
      client.zendeskConfig.apiToken
    );

    const result = await new Promise((resolve, reject) => {
      zendeskClient.search.query(query, (err, req, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);
        }
      });
    });

    res.json(result);
  } catch (error) {
    winston.error('Error searching tickets:', error);
    res.status(500).json({ error: 'Failed to search tickets' });
  }
});

// Helper function to get client configuration
async function getClientConfig(clientId) {
  // Implement this function to fetch client configuration from your database
  // This should return an object with zendeskConfig containing subdomain, email, and apiToken
  throw new Error('Not implemented');
}

module.exports = router;
