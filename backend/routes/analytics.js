const express = require('express');
const Score = require('../models/Score');
const Quiz = require('../models/Quiz');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Get user analytics
router.get('/', authenticateToken, async (req, res) => {
  try {
    const userId = req.user._id;

    // Get user's quiz scores
    const scores = await Score.find({ user: userId }).populate('quiz', 'title');
    const totalQuizzes = scores.length;
    const averageScore = totalQuizzes > 0 ? scores.reduce((sum, score) => sum + score.score, 0) / totalQuizzes : 0;

    // Get performance by category
    const categoryPerformance = {};
    scores.forEach(score => {
      const category = score.quiz.category || 'General';
      if (!categoryPerformance[category]) {
        categoryPerformance[category] = { total: 0, count: 0 };
      }
      categoryPerformance[category].total += score.score;
      categoryPerformance[category].count += 1;
    });

    Object.keys(categoryPerformance).forEach(cat => {
      categoryPerformance[cat].average = categoryPerformance[cat].total / categoryPerformance[cat].count;
    });

    res.json({
      totalQuizzes,
      averageScore: Math.round(averageScore * 100) / 100,
      categoryPerformance,
      recentScores: scores.slice(-5).reverse() // Last 5 scores
    });
  } catch (error) {
    console.error('Error fetching analytics:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
