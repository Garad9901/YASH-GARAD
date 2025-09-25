const express = require('express');
const Quiz = require('../models/Quiz');
const Score = require('../models/Score');
const { body, validationResult } = require('express-validator');
const { authorizeRoles } = require('../middleware/auth');

const router = express.Router();

// Get all quizzes (with optional filters)
router.get('/', async (req, res) => {
  try {
    const { company, category, difficulty } = req.query;
    const filter = {};

    if (company) filter.company = company;
    if (category) filter.category = category;
    if (difficulty) filter.difficulty = difficulty;

    const quizzes = await Quiz.find(filter).select('-questions');
    res.json(quizzes);
  } catch (error) {
    console.error('Error fetching quizzes:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Get quiz by ID with questions
router.get('/:id', async (req, res) => {
  try {
    const quiz = await Quiz.findById(req.params.id);
    if (!quiz) {
      return res.status(404).json({ error: 'Quiz not found' });
    }
    res.json(quiz);
  } catch (error) {
    console.error('Error fetching quiz:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Create a new quiz (Admin or Mentor only)
router.post('/', authorizeRoles('Admin', 'Mentor'), [
  body('title').notEmpty().withMessage('Title is required'),
  body('description').notEmpty().withMessage('Description is required'),
  body('company').notEmpty().withMessage('Company is required'),
  body('category').notEmpty().withMessage('Category is required'),
  body('totalQuestions').isInt({ min: 1 }).withMessage('Total questions must be at least 1'),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  try {
    const quizData = req.body;
    quizData.createdBy = req.user._id;

    const quiz = new Quiz(quizData);
    await quiz.save();

    res.status(201).json(quiz);
  } catch (error) {
    console.error('Error creating quiz:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Update quiz (Admin or Mentor only)
router.put('/:id', authorizeRoles('Admin', 'Mentor'), async (req, res) => {
  try {
    const quiz = await Quiz.findById(req.params.id);
    if (!quiz) {
      return res.status(404).json({ error: 'Quiz not found' });
    }

    Object.assign(quiz, req.body);
    await quiz.save();

    res.json(quiz);
  } catch (error) {
    console.error('Error updating quiz:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Delete quiz (Admin only)
router.delete('/:id', authorizeRoles('Admin'), async (req, res) => {
  try {
    const quiz = await Quiz.findByIdAndDelete(req.params.id);
    if (!quiz) {
      return res.status(404).json({ error: 'Quiz not found' });
    }
    res.json({ message: 'Quiz deleted successfully' });
  } catch (error) {
    console.error('Error deleting quiz:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
