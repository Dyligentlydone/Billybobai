const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../src/index');
const aiService = require('../src/services/aiService');

describe('AI Routes', () => {
  beforeAll(async () => {
    // Connect to test database
    await mongoose.connect(process.env.MONGODB_URI_TEST);
  });

  afterAll(async () => {
    // Disconnect after tests
    await mongoose.connection.close();
  });

  describe('POST /api/ai/analyze', () => {
    it('should analyze workflow request', async () => {
      const input = 'CoffeeShop123 needs email automation and a website chatbot';
      
      const response = await request(app)
        .post('/api/ai/analyze')
        .send({ input })
        .expect(200);

      expect(response.body).toHaveProperty('channels');
      expect(response.body.channels).toContain('email');
      expect(response.body).toHaveProperty('estimatedCosts');
      expect(response.body).toHaveProperty('suggestedTemplates');
    });

    it('should return 400 for empty input', async () => {
      await request(app)
        .post('/api/ai/analyze')
        .send({})
        .expect(400);
    });
  });

  describe('POST /api/ai/feedback', () => {
    it('should save feedback', async () => {
      const feedback = {
        originalInput: 'test input',
        originalOutput: { channels: ['email'] },
        correctedOutput: { channels: ['email', 'sms'] },
        notes: 'Added SMS channel'
      };

      const response = await request(app)
        .post('/api/ai/feedback')
        .send(feedback)
        .expect(200);

      expect(response.body).toHaveProperty('message', 'Feedback saved successfully');
    });
  });

  describe('POST /api/ai/instructions', () => {
    it('should generate setup instructions', async () => {
      const workflow = {
        channels: ['email', 'sms'],
        triggers: {
          'new_order': {
            actions: [
              { type: 'sendgrid.email', template: 'order_confirmation' },
              { type: 'twilio.sms', template: 'order_confirmation_sms' }
            ]
          }
        }
      };

      const response = await request(app)
        .post('/api/ai/instructions')
        .send({ workflow })
        .expect(200);

      expect(response.body).toHaveProperty('instructions');
      expect(Array.isArray(response.body.instructions)).toBe(true);
    });
  });
});
