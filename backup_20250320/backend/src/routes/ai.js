const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const winston = require('winston');
const openai = require('../services/openai');
const Feedback = require('../models/feedback');
const templates = require('../data/templates.json');

// AI Analysis endpoint
router.post('/analyze', [
  body('input').isString().notEmpty(),
  body('clientId').isString().notEmpty()
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { input, clientId } = req.body;
    const workflow = await generateWorkflow(input, clientId);
    const instructions = await generateInstructions(workflow);

    res.json({
      workflow,
      instructions,
      estimatedCosts: calculateCosts(workflow),
      suggestedTemplates: findMatchingTemplates(workflow)
    });
  } catch (error) {
    winston.error('Error in AI analysis:', error);
    res.status(500).json({ error: 'Failed to analyze input' });
  }
});

// Save feedback
router.post('/feedback', [
  body('originalInput').isString().notEmpty(),
  body('originalOutput').isObject(),
  body('correctedOutput').isObject(),
  body('notes').isString()
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const feedback = new Feedback(req.body);
    await feedback.save();
    res.json({ message: 'Feedback saved successfully' });
  } catch (error) {
    winston.error('Error saving feedback:', error);
    res.status(500).json({ error: 'Failed to save feedback' });
  }
});

// Generate workflow from input
async function generateWorkflow(input, clientId) {
  const prompt = {
    role: 'system',
    content: `You are an AI assistant that generates customer service automation workflows. 
    Analyze the input and create a structured workflow using Twilio (SMS, Voice, Flex), 
    SendGrid (Email), and Zendesk (Tickets). Include triggers, conditions, and actions.`
  };

  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [
      prompt,
      {
        role: 'user',
        content: `Generate a workflow for: ${input}`
      }
    ],
    temperature: 0.7,
    max_tokens: 1000
  });

  const rawWorkflow = JSON.parse(response.choices[0].message.content);
  return validateAndEnhanceWorkflow(rawWorkflow);
}

// Generate setup instructions
async function generateInstructions(workflow) {
  const instructions = [];

  // Twilio setup
  if (workflow.twilio) {
    if (workflow.twilio.sms) {
      instructions.push({
        integration: 'Twilio',
        step: 'Configure SMS webhook',
        action: 'Set webhook URL to /api/integrations/twilio/sms'
      });
    }
    if (workflow.twilio.voice) {
      instructions.push({
        integration: 'Twilio',
        step: 'Configure Voice webhook',
        action: 'Set webhook URL to /api/integrations/twilio/voice'
      });
    }
    if (workflow.twilio.flex) {
      instructions.push({
        integration: 'Twilio',
        step: 'Configure Flex webhook',
        action: 'Set webhook URL to /api/integrations/twilio/flex'
      });
    }
  }

  // SendGrid setup
  if (workflow.sendgrid?.email) {
    instructions.push({
      integration: 'SendGrid',
      step: 'Configure Email webhook',
      action: 'Set webhook URL to /api/integrations/sendgrid/webhook'
    });
  }

  // Zendesk setup
  if (workflow.zendesk?.ticket) {
    instructions.push({
      integration: 'Zendesk',
      step: 'Configure Zendesk webhook',
      action: 'Set webhook URL to /api/integrations/zendesk/webhook'
    });
  }

  return instructions;
}

// Calculate estimated costs
function calculateCosts(workflow) {
  const costs = {
    twilio: {
      sms: 0,
      voice: 0,
      flex: 0
    },
    sendgrid: {
      email: 0
    },
    zendesk: {
      ticket: 0
    }
  };

  // Twilio costs
  if (workflow.twilio) {
    if (workflow.twilio.sms) {
      costs.twilio.sms = 0.0075; // Per message
    }
    if (workflow.twilio.voice) {
      costs.twilio.voice = 0.0085; // Per minute
    }
    if (workflow.twilio.flex) {
      costs.twilio.flex = 1; // Per active user per hour
    }
  }

  // SendGrid costs
  if (workflow.sendgrid?.email) {
    costs.sendgrid.email = 0.0001; // Per email
  }

  // Zendesk costs
  if (workflow.zendesk?.ticket) {
    costs.zendesk.ticket = 0.5; // Per ticket
  }

  return costs;
}

// Find matching templates
function findMatchingTemplates(workflow) {
  return templates.filter(template => {
    // Check if template matches workflow requirements
    const matchScore = calculateTemplateMatch(template, workflow);
    return matchScore > 0.7; // Return templates with >70% match
  });
}

// Calculate template match score
function calculateTemplateMatch(template, workflow) {
  let matchPoints = 0;
  let totalPoints = 0;

  // Check Twilio features
  if (workflow.twilio) {
    totalPoints += 3;
    if (template.twilio?.sms === workflow.twilio.sms) matchPoints++;
    if (template.twilio?.voice === workflow.twilio.voice) matchPoints++;
    if (template.twilio?.flex === workflow.twilio.flex) matchPoints++;
  }

  // Check SendGrid features
  if (workflow.sendgrid) {
    totalPoints++;
    if (template.sendgrid?.email === workflow.sendgrid.email) matchPoints++;
  }

  // Check Zendesk features
  if (workflow.zendesk) {
    totalPoints++;
    if (template.zendesk?.ticket === workflow.zendesk.ticket) matchPoints++;
  }

  return totalPoints > 0 ? matchPoints / totalPoints : 0;
}

// Validate and enhance workflow
function validateAndEnhanceWorkflow(workflow) {
  // Add default values and validate structure
  const enhanced = {
    twilio: {
      sms: workflow.twilio?.sms || null,
      voice: workflow.twilio?.voice || null,
      flex: workflow.twilio?.flex || null
    },
    sendgrid: {
      email: workflow.sendgrid?.email || null
    },
    zendesk: {
      ticket: workflow.zendesk?.ticket || null
    },
    triggers: workflow.triggers || {},
    conditions: workflow.conditions || {},
    actions: workflow.actions || []
  };

  // Validate and enhance triggers
  Object.keys(enhanced.triggers).forEach(trigger => {
    if (!enhanced.triggers[trigger].actions) {
      enhanced.triggers[trigger].actions = [];
    }
  });

  return enhanced;
}

module.exports = router;
