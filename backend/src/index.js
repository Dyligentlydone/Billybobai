require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const winston = require('winston');

const clientRoutes = require('./routes/clients');
const workflowRoutes = require('./routes/workflows');
const aiRoutes = require('./routes/ai');
const analyticsRoutes = require('./routes/analytics');
const twilioRoutes = require('./routes/integrations/twilio');
const sendgridRoutes = require('./routes/integrations/sendgrid');
const zendeskRoutes = require('./routes/integrations/zendesk');

// Configure Winston logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

const app = express();

// Middleware
app.use(helmet());
app.use(cors({
  origin: 'https://dyligent.xyz',
  credentials: true
}));
app.use(express.json());
app.use(morgan('combined'));

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error(err.stack);
  res.status(500).send('Something broke!');
});

// Routes
app.use('/api/clients', clientRoutes);
app.use('/api/workflows', workflowRoutes);
app.use('/api/ai', aiRoutes);
app.use('/api/analytics', analyticsRoutes);
app.use('/api/integrations/twilio', twilioRoutes);
app.use('/api/integrations/sendgrid', sendgridRoutes);
app.use('/api/integrations/zendesk', zendeskRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI)
  .then(() => {
    logger.info('Connected to MongoDB');
  })
  .catch((err) => {
    logger.error('MongoDB connection error:', err);
    process.exit(1);
  });

// Start server
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  logger.info(`Server is running on port ${PORT}`);
});
