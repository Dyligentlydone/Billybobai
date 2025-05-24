const express = require('express');
const router = express.Router();
const Client = require('../models/Client');
const winston = require('winston');

// Get all clients
router.get('/', async (req, res) => {
  try {
    const filter = {};
    if (req.query.business_id) {
      filter.businessId = req.query.business_id;
    }
    const clients = await Client.find(filter).select('-twilioConfig.authToken -sendgridConfig.apiKey -zendeskConfig.apiToken');
    res.json({ clients });
  } catch (error) {
    winston.error('Error fetching clients:', error);
    res.status(500).json({ error: 'Failed to fetch clients' });
  }
});

// Create new client
router.post('/', async (req, res) => {
  try {
    const {
      name,
      twilioConfig,
      sendgridConfig,
      zendeskConfig
    } = req.body;

    // Validate required fields
    if (!name) {
      return res.status(400).json({ error: 'Client name is required' });
    }

    const client = new Client({
      name,
      twilioConfig: twilioConfig || {},
      sendgridConfig: sendgridConfig || {},
      zendeskConfig: zendeskConfig || {}
    });

    await client.save();
    
    // Return client without sensitive data
    const clientResponse = client.toObject();
    delete clientResponse.twilioConfig.authToken;
    delete clientResponse.sendgridConfig.apiKey;
    delete clientResponse.zendeskConfig.apiToken;
    
    res.status(201).json(clientResponse);
  } catch (error) {
    winston.error('Error creating client:', error);
    res.status(500).json({ error: 'Failed to create client' });
  }
});

// Get client by ID
router.get('/:id', async (req, res) => {
  try {
    const client = await Client.findById(req.params.id)
      .select('-twilioConfig.authToken -sendgridConfig.apiKey -zendeskConfig.apiToken');
    
    if (!client) {
      return res.status(404).json({ error: 'Client not found' });
    }
    
    res.json(client);
  } catch (error) {
    winston.error('Error fetching client:', error);
    res.status(500).json({ error: 'Failed to fetch client' });
  }
});

// Update client
router.put('/:id', async (req, res) => {
  try {
    const {
      name,
      twilioConfig,
      sendgridConfig,
      zendeskConfig
    } = req.body;

    const client = await Client.findById(req.params.id);
    if (!client) {
      return res.status(404).json({ error: 'Client not found' });
    }

    // Update only provided fields
    if (name) client.name = name;
    if (twilioConfig) {
      client.twilioConfig = {
        ...client.twilioConfig,
        ...twilioConfig
      };
    }
    if (sendgridConfig) {
      client.sendgridConfig = {
        ...client.sendgridConfig,
        ...sendgridConfig
      };
    }
    if (zendeskConfig) {
      client.zendeskConfig = {
        ...client.zendeskConfig,
        ...zendeskConfig
      };
    }

    await client.save();
    
    // Return updated client without sensitive data
    const clientResponse = client.toObject();
    delete clientResponse.twilioConfig.authToken;
    delete clientResponse.sendgridConfig.apiKey;
    delete clientResponse.zendeskConfig.apiToken;
    
    res.json(clientResponse);
  } catch (error) {
    winston.error('Error updating client:', error);
    res.status(500).json({ error: 'Failed to update client' });
  }
});

// Delete client
router.delete('/:id', async (req, res) => {
  try {
    const client = await Client.findById(req.params.id);
    if (!client) {
      return res.status(404).json({ error: 'Client not found' });
    }

    await client.deleteOne();
    res.json({ message: 'Client deleted successfully' });
  } catch (error) {
    winston.error('Error deleting client:', error);
    res.status(500).json({ error: 'Failed to delete client' });
  }
});

// Validate client credentials
router.post('/:id/validate', async (req, res) => {
  try {
    const client = await Client.findById(req.params.id);
    if (!client) {
      return res.status(404).json({ error: 'Client not found' });
    }

    const validationResults = {
      twilio: false,
      sendgrid: false,
      zendesk: false
    };

    // Validate Twilio credentials if they exist
    if (client.twilioConfig.accountSid && client.twilioConfig.authToken) {
      try {
        const twilio = require('twilio')(
          client.twilioConfig.accountSid,
          client.twilioConfig.authToken
        );
        await twilio.api.accounts(client.twilioConfig.accountSid).fetch();
        validationResults.twilio = true;
      } catch (error) {
        winston.error('Twilio validation error:', error);
      }
    }

    // Validate SendGrid credentials if they exist
    if (client.sendgridConfig.apiKey) {
      try {
        const sgMail = require('@sendgrid/mail');
        sgMail.setApiKey(client.sendgridConfig.apiKey);
        await sgMail.get('version');
        validationResults.sendgrid = true;
      } catch (error) {
        winston.error('SendGrid validation error:', error);
      }
    }

    // Validate Zendesk credentials if they exist
    if (client.zendeskConfig.subdomain && client.zendeskConfig.apiToken) {
      try {
        const axios = require('axios');
        await axios.get(
          `https://${client.zendeskConfig.subdomain}.zendesk.com/api/v2/users/me`,
          {
            headers: {
              Authorization: `Bearer ${client.zendeskConfig.apiToken}`
            }
          }
        );
        validationResults.zendesk = true;
      } catch (error) {
        winston.error('Zendesk validation error:', error);
      }
    }

    res.json(validationResults);
  } catch (error) {
    winston.error('Error validating client credentials:', error);
    res.status(500).json({ error: 'Failed to validate client credentials' });
  }
});

module.exports = router;
