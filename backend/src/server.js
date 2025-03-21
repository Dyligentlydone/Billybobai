require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
const connectDB = require('./config/database');

// Initialize Express app
const app = express();

// Configure Winston logger
winston.configure({
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ]
});

// Connect to MongoDB
connectDB();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api', limiter);

// Routes (to be implemented)
app.use('/api/auth', require('./routes/auth'));
app.use('/api/workflows', require('./routes/workflows'));
app.use('/api/clients', require('./routes/clients'));
app.use('/api/integrations', require('./routes/integrations'));

// Error handling middleware
app.use((err, req, res, next) => {
  winston.error(err.stack);
  res.status(500).send('Something broke!');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  winston.info(`Server is running on port ${PORT}`);
});
