const express = require('express');
const router = express.Router();
const Workflow = require('../models/Workflow');
const aiService = require('../services/aiService');
const winston = require('winston');

// Get all workflows
router.get('/', async (req, res) => {
  try {
    const workflows = await Workflow.find().populate('client', 'name');
    res.json(workflows);
  } catch (error) {
    winston.error('Error fetching workflows:', error);
    res.status(500).json({ error: 'Failed to fetch workflows' });
  }
});

// Analyze natural language input
router.post('/analyze', async (req, res) => {
  try {
    const { input } = req.body;
    if (!input) {
      return res.status(400).json({ error: 'Input is required' });
    }

    const analysis = await aiService.analyzeWorkflowRequest(input);
    res.json(analysis);
  } catch (error) {
    winston.error('Error analyzing workflow:', error);
    res.status(500).json({ error: 'Failed to analyze workflow' });
  }
});

// Create new workflow
router.post('/', async (req, res) => {
  try {
    const { 
      name,
      clientId,
      naturalLanguageInput,
      channels,
      configuration,
      zendeskIntegration
    } = req.body;

    const workflow = new Workflow({
      name,
      client: clientId,
      naturalLanguageInput,
      channels,
      configuration,
      zendeskIntegration
    });

    await workflow.save();
    res.status(201).json(workflow);
  } catch (error) {
    winston.error('Error creating workflow:', error);
    res.status(500).json({ error: 'Failed to create workflow' });
  }
});

// Get workflow by ID
router.get('/:id', async (req, res) => {
  try {
    const workflow = await Workflow.findById(req.params.id).populate('client');
    if (!workflow) {
      return res.status(404).json({ error: 'Workflow not found' });
    }
    res.json(workflow);
  } catch (error) {
    winston.error('Error fetching workflow:', error);
    res.status(500).json({ error: 'Failed to fetch workflow' });
  }
});

module.exports = router;
