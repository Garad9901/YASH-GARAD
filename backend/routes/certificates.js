const express = require('express');
const Certificate = require('../models/Certificate');
const Score = require('../models/Score');
const { authorizeRoles } = require('../middleware/auth');

const router = express.Router();

// Get user's certificates
router.get('/', async (req, res) => {
  try {
    const certificates = await Certificate.find({ user: req.user._id, isActive: true });
    res.json(certificates);
  } catch (error) {
    console.error('Error fetching certificates:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Generate certificate for quiz completion
router.post('/generate', async (req, res) => {
  try {
    const { quizId } = req.body;

    // Check if user has completed the quiz with passing score
    const score = await Score.findOne({ user: req.user._id, quiz: quizId }).sort({ completedAt: -1 });
    if (!score || score.score < 60) {
      return res.status(400).json({ error: 'Quiz not completed with passing score' });
    }

    // Check if certificate already exists
    const existingCert = await Certificate.findOne({ user: req.user._id, quiz: quizId });
    if (existingCert) {
      return res.status(409).json({ error: 'Certificate already exists' });
    }

    // Generate certificate
    const certificate = new Certificate({
      user: req.user._id,
      title: `Quiz Completion Certificate`,
      description: `Successfully completed quiz with ${score.score}% score`,
      type: 'quiz_completion',
      quiz: quizId,
      score: score.score
    });

    await certificate.save();

    res.status(201).json(certificate);
  } catch (error) {
    console.error('Error generating certificate:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Get certificate by ID
router.get('/:id', async (req, res) => {
  try {
    const certificate = await Certificate.findById(req.params.id).populate('user', 'firstName lastName');
    if (!certificate) {
      return res.status(404).json({ error: 'Certificate not found' });
    }
    res.json(certificate);
  } catch (error) {
    console.error('Error fetching certificate:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
