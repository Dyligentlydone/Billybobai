const mongoose = require('mongoose');

const feedbackSchema = new mongoose.Schema({
  originalInput: {
    type: String,
    required: true
  },
  originalOutput: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  correctedOutput: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  notes: {
    type: String
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  status: {
    type: String,
    enum: ['pending', 'reviewed', 'implemented'],
    default: 'pending'
  }
});

module.exports = mongoose.model('Feedback', feedbackSchema);
