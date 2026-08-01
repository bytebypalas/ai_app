/**
 * Prediction Model Logic for EduPredict AI
 * Simulates the ML prediction pipeline with realistic calculations
 */

import { performanceLevels, gradeScale } from '../data/sampleData'

/**
 * Calculate predicted percentage based on input features
 * Uses weighted formula simulating a trained ML model
 */
export function predictPerformance(studentData) {
  const weights = {
    attendance: 0.20,
    studyHours: 0.18,
    prevMarks: 0.12,
    internalMarks: 0.12,
    assignmentScore: 0.10,
    labScore: 0.08,
    backlogs: -0.10,
    gpa: 0.15,
    sleepHours: 0.05,
    participation: 0.06,
    submissionRate: 0.08,
  }

  // Normalize values to 0-1 scale
  const normalized = {
    attendance: studentData.attendance / 100,
    studyHours: Math.min(studentData.studyHours / 12, 1),
    prevMarks: studentData.prevMarks / 100,
    internalMarks: studentData.internalMarks / 100,
    assignmentScore: studentData.assignmentScore / 100,
    labScore: studentData.labScore / 100,
    backlogs: Math.min(studentData.backlogs / 10, 1),
    gpa: studentData.gpa / 10,
    sleepHours: Math.min(studentData.sleepHours / 10, 1),
    participation: studentData.participation / 100,
    submissionRate: studentData.submissionRate / 100,
  }

  // Calculate weighted score
  let score = 0
  score += normalized.attendance * weights.attendance
  score += normalized.studyHours * weights.studyHours
  score += normalized.prevMarks * weights.prevMarks
  score += normalized.internalMarks * weights.internalMarks
  score += normalized.assignmentScore * weights.assignmentScore
  score += normalized.labScore * weights.labScore
  score += (1 - normalized.backlogs) * Math.abs(weights.backlogs) // Invert backlogs (more = worse)
  score += normalized.gpa * weights.gpa
  score += normalized.sleepHours * weights.sleepHours
  score += normalized.participation * weights.participation
  score += normalized.submissionRate * weights.submissionRate

  // Add some controlled randomness to simulate model variance
  const noise = (Math.random() - 0.5) * 0.04
  score = Math.max(0, Math.min(1, score + noise))

  // Convert to percentage
  const percentage = Math.round(score * 1000) / 10

  return percentage
}

/**
 * Get grade based on percentage
 */
export function getGrade(percentage) {
  const found = gradeScale.find(g => percentage >= g.min && percentage <= g.max)
  return found || gradeScale[gradeScale.length - 1]
}

/**
 * Get performance level based on percentage
 */
export function getPerformanceLevel(percentage) {
  const found = performanceLevels.find(p => percentage >= p.min && percentage <= p.max)
  return found || performanceLevels[performanceLevels.length - 1]
}

/**
 * Calculate confidence score based on how close values are to ideal
 */
export function calculateConfidence(studentData) {
  const idealScores = {
    attendance: 90,
    studyHours: 7,
    prevMarks: 85,
    internalMarks: 80,
    assignmentScore: 85,
    labScore: 80,
    backlogs: 0,
    gpa: 8.5,
    sleepHours: 7.5,
    participation: 80,
    submissionRate: 90,
  }

  let totalDeviation = 0
  let count = 0

  for (const [key, ideal] of Object.entries(idealScores)) {
    const actual = studentData[key] || 0
    const maxVal = key === 'studyHours' ? 12 : key === 'sleepHours' ? 10 : key === 'gpa' ? 10 : key === 'backlogs' ? 10 : 100
    const normalizedActual = actual / maxVal
    const normalizedIdeal = ideal / maxVal
    totalDeviation += Math.abs(normalizedActual - normalizedIdeal)
    count++
  }

  const avgDeviation = totalDeviation / count
  const confidence = Math.max(60, Math.min(99, (1 - avgDeviation) * 100))
  return Math.round(confidence * 10) / 10
}

/**
 * Calculate risk level based on the input data
 */
export function calculateRiskLevel(studentData) {
  let riskScore = 0

  if (studentData.attendance < 60) riskScore += 30
  else if (studentData.attendance < 75) riskScore += 15

  if (studentData.studyHours < 3) riskScore += 25
  else if (studentData.studyHours < 5) riskScore += 12

  if (studentData.backlogs > 3) riskScore += 25
  else if (studentData.backlogs > 1) riskScore += 12

  if (studentData.gpa < 5) riskScore += 25
  else if (studentData.gpa < 6.5) riskScore += 12

  if (studentData.submissionRate < 60) riskScore += 20
  else if (studentData.submissionRate < 80) riskScore += 10

  if (riskScore >= 60) return 'High'
  if (riskScore >= 30) return 'Medium'
  return 'Low'
}

/**
 * Check if student passes (percentage >= 50)
 */
export function checkPassStatus(percentage) {
  return percentage >= 50 ? 'Pass' : 'Fail'
}

/**
 * Generate probability distribution across performance categories
 */
export function calculateProbabilities(percentage) {
  const categories = ['Poor', 'Average', 'Good', 'Excellent']
  const centers = [25, 50, 72, 90]
  const spread = 15

  let probs = categories.map((cat, i) => {
    const dist = Math.abs(percentage - centers[i])
    const rawProb = Math.exp(-(dist * dist) / (2 * spread * spread))
    return { category: cat, probability: rawProb * 100 }
  })

  // Normalize to sum to 100%
  const total = probs.reduce((sum, p) => sum + p.probability, 0)
  probs = probs.map(p => ({
    ...p,
    probability: Math.round((p.probability / total) * 1000) / 10
  }))

  return probs
}

/**
 * Full prediction pipeline
 */
export function runPrediction(studentData) {
  const percentage = predictPerformance(studentData)
  const gradeInfo = getGrade(percentage)
  const levelInfo = getPerformanceLevel(percentage)
  const confidence = calculateConfidence(studentData)
  const riskLevel = calculateRiskLevel(studentData)
  const status = checkPassStatus(percentage)
  const probabilities = calculateProbabilities(percentage)

  return {
    percentage,
    grade: gradeInfo.grade,
    gradeDescription: gradeInfo.description,
    performanceLevel: levelInfo.level,
    performanceColor: levelInfo.color,
    confidence,
    riskLevel,
    status,
    probabilities,
    timestamp: new Date().toISOString(),
  }
}

