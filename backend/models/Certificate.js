const mongoose = require('mongoose');

const certificateSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  type: {
    type: String,
    enum: ['quiz_completion', 'course_completion', 'achievement'],
    default: 'quiz_completion'
  },
  quiz: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Quiz'
  },
  score: {
    type: Number,
    min: 0,
    max: 100
  },
  blockchainHash: {
    type: String,
    unique: true
  },
  certificateUrl: {
    type: String
  },
  issuedAt: {
    type: Date,
    default: Date.now
  },
  expiresAt: {
    type: Date
  },
  issuer: {
    type: String,
    default: 'AI Educational Platform'
  },
  isActive: {
    type: Boolean,
    default: true
  }
});

// Index for better query performance
certificateSchema.index({ user: 1 });
certificateSchema.index({ blockchainHash: 1 });

module.exports = mongoose.model('Certificate', certificateSchema);
