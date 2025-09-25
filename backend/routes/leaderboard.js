const express = require('express');
const Leaderboard = require('../models/Leaderboard');
const User = require('../models/User');

const router = express.Router();

// Get global leaderboard
router.get('/', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;
    const leaderboard = await Leaderboard.find()
      .populate('user', 'firstName lastName username')
      .sort({ totalScore: -1, averageScore: -1 })
      .limit(limit);

    res.json(leaderboard);
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Get user's rank
router.get('/rank/:userId', async (req, res) => {
  try {
    const userId = req.params.userId;
    const userEntry = await Leaderboard.findOne({ user: userId });

    if (!userEntry) {
      return res.json({ rank: null, message: 'User not found in leaderboard' });
    }

    const higherScores = await Leaderboard.countDocuments({
      totalScore: { $gt: userEntry.totalScore }
    });

    const sameScoreHigherAvg = await Leaderboard.countDocuments({
      totalScore: userEntry.totalScore,
      averageScore: { $gt: userEntry.averageScore }
    });

    const rank = higherScores + sameScoreHigherAvg + 1;

    res.json({ rank, ...userEntry.toObject() });
  } catch (error) {
    console.error('Error fetching user rank:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
