const mongoose = require('mongoose');

const leaderboardSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  totalScore: {
    type: Number,
    default: 0
  },
  quizzesCompleted: {
    type: Number,
    default: 0
  },
  averageScore: {
    type: Number,
    default: 0
  },
  rank: {
    type: Number
  },
  lastUpdated: {
    type: Date,
    default: Date.now
  }
});

// Index for better query performance
leaderboardSchema.index({ totalScore: -1 });
leaderboardSchema.index({ averageScore: -1 });

module.exports = mongoose.model('Leaderboard', leaderboardSchema);
