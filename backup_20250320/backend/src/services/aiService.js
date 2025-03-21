const OpenAI = require('openai');
const winston = require('winston');

const openai = new OpenAI(process.env.OPENAI_API_KEY);

class AIService {
  async analyzeWorkflowRequest(input) {
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: `You are an AI assistant that analyzes customer service automation requests and converts them into structured workflow configurations.
            Focus on identifying:
            1. Required channels (email, sms, voice, webchat, whatsapp)
            2. Key automation triggers and responses
            3. Integration requirements
            4. Suggested templates and flows
            Output in JSON format.`
          },
          {
            role: "user",
            content: input
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      });

      const analysis = JSON.parse(response.choices[0].message.content);
      return this.validateAndEnrichAnalysis(analysis);
    } catch (error) {
      winston.error('Error analyzing workflow request:', error);
      throw new Error('Failed to analyze workflow request');
    }
  }

  validateAndEnrichAnalysis(analysis) {
    // Add cost estimation
    analysis.estimatedCosts = this.calculateEstimatedCosts(analysis);
    
    // Add template suggestions
    analysis.suggestedTemplates = this.getSuggestedTemplates(analysis);
    
    return analysis;
  }

  calculateEstimatedCosts(analysis) {
    const costs = {
      sms: 0.0075,    // per message
      email: 0.001,   // per email
      voice: 0.015,   // per minute
      whatsapp: 0.005 // per message
    };

    // Estimate based on channels and expected volume
    // This is a basic estimation that should be enhanced based on actual usage patterns
    return {
      monthly: {
        sms: analysis.channels.includes('sms') ? costs.sms * 1000 : 0,
        email: analysis.channels.includes('email') ? costs.email * 5000 : 0,
        voice: analysis.channels.includes('voice') ? costs.voice * 1000 : 0,
        whatsapp: analysis.channels.includes('whatsapp') ? costs.whatsapp * 500 : 0
      }
    };
  }

  getSuggestedTemplates(analysis) {
    // Return relevant templates based on the use case
    // This should be expanded with a proper template database
    return {
      email: [
        {
          name: 'Order Confirmation',
          subject: 'Your order has been confirmed',
          content: 'Dear {{customer_name}},\n\nThank you for your order...'
        }
      ],
      sms: [
        {
          name: 'Appointment Reminder',
          content: 'Reminder: Your appointment is scheduled for {{appointment_time}}...'
        }
      ]
    };
  }
}

module.exports = new AIService();
