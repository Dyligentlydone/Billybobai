const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../src/index');
const twilio = require('twilio');
const sgMail = require('@sendgrid/mail');
const zendesk = require('node-zendesk');

// Mock external services
jest.mock('twilio');
jest.mock('@sendgrid/mail');
jest.mock('node-zendesk');

describe('Integration Routes', () => {
  beforeAll(async () => {
    await mongoose.connect(process.env.MONGODB_URI_TEST);
  });

  afterAll(async () => {
    await mongoose.connection.close();
  });

  describe('Twilio Integration', () => {
    describe('POST /api/integrations/twilio/sms', () => {
      it('should process incoming SMS', async () => {
        const mockTwiml = {
          message: jest.fn(),
          toString: () => '<Response><Message>Thank you</Message></Response>'
        };

        twilio.twiml.MessagingResponse.mockImplementation(() => mockTwiml);

        const response = await request(app)
          .post('/api/integrations/twilio/sms')
          .send({
            Body: 'Test message',
            From: '+1234567890'
          })
          .expect(200);

        expect(response.text).toContain('<Response>');
        expect(mockTwiml.message).toHaveBeenCalled();
      });
    });

    describe('POST /api/integrations/twilio/send-sms', () => {
      it('should send SMS', async () => {
        const mockMessage = { sid: 'test_sid' };
        twilio().messages.create.mockResolvedValue(mockMessage);

        const response = await request(app)
          .post('/api/integrations/twilio/send-sms')
          .send({
            to: '+1234567890',
            message: 'Test message',
            clientId: 'test_client'
          })
          .expect(200);

        expect(response.body).toHaveProperty('sid', 'test_sid');
      });
    });
  });

  describe('SendGrid Integration', () => {
    describe('POST /api/integrations/sendgrid/send', () => {
      it('should send email', async () => {
        const mockResponse = [{ statusCode: 202 }];
        sgMail.send.mockResolvedValue(mockResponse);

        const response = await request(app)
          .post('/api/integrations/sendgrid/send')
          .send({
            to: 'test@example.com',
            subject: 'Test Email',
            templateId: 'd-test123',
            dynamicTemplateData: { name: 'Test User' },
            clientId: 'test_client'
          })
          .expect(200);

        expect(response.body[0]).toHaveProperty('statusCode', 202);
      });
    });

    describe('POST /api/integrations/sendgrid/templates', () => {
      it('should create template', async () => {
        const mockTemplate = { id: 'template_id' };
        const mockVersion = { id: 'version_id' };

        sgMail.request
          .mockResolvedValueOnce([{ body: mockTemplate }])
          .mockResolvedValueOnce([{ body: mockVersion }]);

        const response = await request(app)
          .post('/api/integrations/sendgrid/templates')
          .send({
            name: 'Test Template',
            subject: 'Test Subject',
            html: '<p>Test content</p>',
            clientId: 'test_client'
          })
          .expect(200);

        expect(response.body).toHaveProperty('templateId', 'template_id');
        expect(response.body).toHaveProperty('versionId', 'version_id');
      });
    });
  });

  describe('Zendesk Integration', () => {
    describe('POST /api/integrations/zendesk/tickets', () => {
      it('should create ticket', async () => {
        const mockTicket = { id: 'ticket_id' };
        zendesk.createClient.mockReturnValue({
          tickets: {
            create: (ticket, callback) => callback(null, null, mockTicket)
          }
        });

        const response = await request(app)
          .post('/api/integrations/zendesk/tickets')
          .send({
            subject: 'Test Ticket',
            description: 'Test description',
            priority: 'normal',
            type: 'incident',
            clientId: 'test_client',
            tags: ['test']
          })
          .expect(200);

        expect(response.body).toHaveProperty('id', 'ticket_id');
      });
    });

    describe('PUT /api/integrations/zendesk/tickets/:id', () => {
      it('should update ticket', async () => {
        const mockTicket = { id: 'ticket_id', status: 'solved' };
        zendesk.createClient.mockReturnValue({
          tickets: {
            update: (id, ticket, callback) => callback(null, null, mockTicket)
          }
        });

        const response = await request(app)
          .put('/api/integrations/zendesk/tickets/ticket_id')
          .send({
            status: 'solved',
            priority: 'high',
            comment: 'Test comment',
            clientId: 'test_client'
          })
          .expect(200);

        expect(response.body).toHaveProperty('status', 'solved');
      });
    });
  });
});
