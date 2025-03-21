const express = require('express');
const router = express.Router();
const { query, validationResult } = require('express-validator');
const twilio = require('twilio');
const sgMail = require('@sendgrid/mail');
const sgClient = require('@sendgrid/client');
const zendesk = require('node-zendesk');
const winston = require('winston');
const { subDays, format, parseISO } = require('date-fns');

// Initialize clients
const twilioClient = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

sgMail.setApiKey(process.env.SENDGRID_API_KEY);
sgClient.setApiKey(process.env.SENDGRID_API_KEY);

// Get analytics data
router.get('/', [
  query('clientId').isString().notEmpty(),
  query('startDate').isString().notEmpty(),
  query('endDate').isString().notEmpty()
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const { clientId, startDate, endDate } = req.query;
    const parsedStartDate = parseISO(startDate);
    const parsedEndDate = parseISO(endDate);

    // Get client's configuration
    const client = await getClientConfig(clientId);

    // Fetch analytics data in parallel
    const [
      twilioAnalytics,
      sendgridAnalytics,
      zendeskAnalytics
    ] = await Promise.all([
      getTwilioAnalytics(client, parsedStartDate, parsedEndDate),
      getSendGridAnalytics(client, parsedStartDate, parsedEndDate),
      getZendeskAnalytics(client, parsedStartDate, parsedEndDate)
    ]);

    // Calculate total costs
    const costs = calculateTotalCosts(twilioAnalytics, sendgridAnalytics, zendeskAnalytics);

    res.json({
      twilio: twilioAnalytics,
      sendgrid: sendgridAnalytics,
      zendesk: zendeskAnalytics,
      costs
    });
  } catch (error) {
    winston.error('Error fetching analytics:', error);
    res.status(500).json({ error: 'Failed to fetch analytics' });
  }
});

// Get Twilio analytics
async function getTwilioAnalytics(client, startDate, endDate) {
  const previousStartDate = subDays(startDate, getDaysDifference(startDate, endDate));

  // Fetch current period data
  const [messages, calls] = await Promise.all([
    twilioClient.messages.list({
      dateSent: {
        $gte: startDate.toISOString(),
        $lte: endDate.toISOString()
      }
    }),
    twilioClient.calls.list({
      startTime: {
        $gte: startDate.toISOString(),
        $lte: endDate.toISOString()
      }
    })
  ]);

  // Fetch previous period data for comparison
  const [previousMessages, previousCalls] = await Promise.all([
    twilioClient.messages.list({
      dateSent: {
        $gte: previousStartDate.toISOString(),
        $lte: startDate.toISOString()
      }
    }),
    twilioClient.calls.list({
      startTime: {
        $gte: previousStartDate.toISOString(),
        $lte: startDate.toISOString()
      }
    })
  ]);

  // Calculate daily message metrics
  const dailyMessages = messages.reduce((acc, message) => {
    const date = format(new Date(message.dateSent), 'yyyy-MM-dd');
    if (!acc[date]) {
      acc[date] = { date, sms: 0, voice: 0 };
    }
    acc[date].sms++;
    return acc;
  }, {});

  // Add voice calls to daily metrics
  calls.forEach(call => {
    const date = format(new Date(call.startTime), 'yyyy-MM-dd');
    if (!dailyMessages[date]) {
      dailyMessages[date] = { date, sms: 0, voice: 0 };
    }
    dailyMessages[date].voice++;
  });

  return {
    totalMessages: messages.length,
    messageChange: calculatePercentageChange(
      messages.length,
      previousMessages.length
    ),
    totalCalls: calls.length,
    callChange: calculatePercentageChange(
      calls.length,
      previousCalls.length
    ),
    dailyMessages: Object.values(dailyMessages).sort((a, b) => a.date.localeCompare(b.date))
  };
}

// Get SendGrid analytics
async function getSendGridAnalytics(client, startDate, endDate) {
  const previousStartDate = subDays(startDate, getDaysDifference(startDate, endDate));

  // Fetch stats for current and previous periods
  const [currentStats, previousStats] = await Promise.all([
    sgClient.request({
      method: 'GET',
      url: '/v3/stats',
      qs: {
        start_date: format(startDate, 'yyyy-MM-dd'),
        end_date: format(endDate, 'yyyy-MM-dd'),
        aggregated_by: 'day'
      }
    }).then(([response]) => response.body),
    sgClient.request({
      method: 'GET',
      url: '/v3/stats',
      qs: {
        start_date: format(previousStartDate, 'yyyy-MM-dd'),
        end_date: format(startDate, 'yyyy-MM-dd'),
        aggregated_by: 'day'
      }
    }).then(([response]) => response.body)
  ]);

  const totalEmails = currentStats.reduce((sum, day) => sum + day.stats[0].metrics.delivered, 0);
  const previousTotalEmails = previousStats.reduce((sum, day) => sum + day.stats[0].metrics.delivered, 0);

  return {
    totalEmails,
    emailChange: calculatePercentageChange(totalEmails, previousTotalEmails),
    emailMetrics: currentStats.map(day => ({
      date: day.date,
      delivered: day.stats[0].metrics.delivered,
      opened: day.stats[0].metrics.opens,
      clicked: day.stats[0].metrics.clicks
    }))
  };
}

// Get Zendesk analytics
async function getZendeskAnalytics(client, startDate, endDate) {
  const zendeskClient = getZendeskClient(client.zendeskConfig);
  const previousStartDate = subDays(startDate, getDaysDifference(startDate, endDate));

  // Fetch tickets for current and previous periods
  const [currentTickets, previousTickets] = await Promise.all([
    new Promise((resolve, reject) => {
      zendeskClient.tickets.list((err, req, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result.filter(ticket => {
            const createdAt = new Date(ticket.created_at);
            return createdAt >= startDate && createdAt <= endDate;
          }));
        }
      });
    }),
    new Promise((resolve, reject) => {
      zendeskClient.tickets.list((err, req, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result.filter(ticket => {
            const createdAt = new Date(ticket.created_at);
            return createdAt >= previousStartDate && createdAt <= startDate;
          }));
        }
      });
    })
  ]);

  return {
    totalTickets: currentTickets.length,
    ticketChange: calculatePercentageChange(
      currentTickets.length,
      previousTickets.length
    ),
    ticketsByPriority: currentTickets.reduce((acc, ticket) => {
      const priority = ticket.priority || 'normal';
      acc[priority] = (acc[priority] || 0) + 1;
      return acc;
    }, {})
  };
}

// Calculate total costs
function calculateTotalCosts(twilioAnalytics, sendgridAnalytics, zendeskAnalytics) {
  const twilioSMSCost = 0.0075; // per message
  const twilioVoiceCost = 0.0085; // per minute
  const sendgridCost = 0.0001; // per email
  const zendeskCost = 0.5; // per ticket

  const current = {
    twilio: {
      current: (twilioAnalytics.totalMessages * twilioSMSCost) +
               (twilioAnalytics.totalCalls * twilioVoiceCost),
      previous: 0,
      breakdown: {
        sms: twilioAnalytics.totalMessages * twilioSMSCost,
        voice: twilioAnalytics.totalCalls * twilioVoiceCost
      }
    },
    sendgrid: {
      current: sendgridAnalytics.totalEmails * sendgridCost,
      previous: 0,
      breakdown: {
        email: sendgridAnalytics.totalEmails * sendgridCost
      }
    },
    zendesk: {
      current: zendeskAnalytics.totalTickets * zendeskCost,
      previous: 0,
      breakdown: {
        tickets: zendeskAnalytics.totalTickets * zendeskCost
      }
    }
  };

  return current;
}

// Helper functions
function calculatePercentageChange(current, previous) {
  if (previous === 0) return 100;
  return ((current - previous) / previous) * 100;
}

function getDaysDifference(startDate, endDate) {
  return Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
}

function getZendeskClient(config) {
  return zendesk.createClient({
    username: config.email,
    token: config.apiToken,
    remoteUri: `https://${config.subdomain}.zendesk.com/api/v2`
  });
}

// Get client configuration
async function getClientConfig(clientId) {
  // For development, return mock configuration
  return {
    twilioConfig: {
      accountSid: process.env.TWILIO_ACCOUNT_SID,
      authToken: process.env.TWILIO_AUTH_TOKEN
    },
    sendgridConfig: {
      apiKey: process.env.SENDGRID_API_KEY
    },
    zendeskConfig: {
      email: process.env.ZENDESK_EMAIL,
      apiToken: process.env.ZENDESK_API_TOKEN,
      subdomain: process.env.ZENDESK_SUBDOMAIN
    }
  };
}

module.exports = router;
