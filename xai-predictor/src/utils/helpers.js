/**
 * Utility helpers for EduPredict AI
 */

/**
 * Format a number with commas
 */
export function formatNumber(num) {
  return num.toLocaleString('en-US')
}

/**
 * Format percentage with one decimal
 */
export function formatPercentage(value) {
  return `${value.toFixed(1)}%`
}

/**
 * Get color based on percentage value
 */
export function getPercentageColor(value) {
  if (value >= 80) return '#10b981'
  if (value >= 60) return '#6366f1'
  if (value >= 40) return '#f59e0b'
  return '#f43f5e'
}

/**
 * Get gradient style from theme
 */
export function getGradient(from = '#6366f1', to = '#8b5cf6') {
  return `linear-gradient(135deg, ${from}, ${to})`
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text, maxLength = 50) {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * Generate a unique ID
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2)
}

/**
 * Class names merger (like clsx)
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(' ')
}

/**
 * Get risk level color
 */
export function getRiskColor(risk) {
  const map = {
    'Low': '#10b981',
    'Medium': '#f59e0b',
    'High': '#f43f5e',
  }
  return map[risk] || '#6366f1'
}

/**
 * Get risk badge class
 */
export function getRiskBadge(risk) {
  const map = {
    'Low': 'badge-low',
    'Medium': 'badge-medium',
    'High': 'badge-high',
  }
  return map[risk] || 'badge-low'
}

/**
 * Get status badge class
 */
export function getStatusBadge(status) {
  return status === 'Pass' ? 'badge-pass' : 'badge-fail'
}

/**
 * Generate recommendations based on student data
 */
export function generateRecommendations(studentData) {
  const recommendations = []

  if (studentData.attendance < 75) {
    recommendations.push({
      icon: '📅',
      category: 'Attendance',
      priority: studentData.attendance < 60 ? 'High' : 'Medium',
      advice: `Increase attendance from ${studentData.attendance}% to at least 75%. Attend all classes and seek help for missed material.`,
    })
  }

  if (studentData.studyHours < 4) {
    recommendations.push({
      icon: '⏰',
      category: 'Study Habits',
      priority: studentData.studyHours < 2 ? 'High' : 'Medium',
      advice: `Increase daily study time from ${studentData.studyHours} hours to at least 5-6 hours. Create a structured study schedule.`,
    })
  }

  if (studentData.backlogs > 0) {
    recommendations.push({
      icon: '⚠️',
      category: 'Backlogs',
      priority: studentData.backlogs > 2 ? 'High' : 'Medium',
      advice: `Clear ${studentData.backlogs} backlog subject(s) by focusing on remedial classes and additional practice.`,
    })
  }

  if (studentData.gpa < 6.5) {
    recommendations.push({
      icon: '🎓',
      category: 'Academic Performance',
      priority: studentData.gpa < 5 ? 'High' : 'Medium',
      advice: `Improve GPA from ${studentData.gpa}/10 to at least 7.0/10. Focus on weak subjects and seek tutoring.`,
    })
  }

  if (studentData.submissionRate < 80) {
    recommendations.push({
      icon: '📤',
      category: 'Assignments',
      priority: studentData.submissionRate < 60 ? 'High' : 'Low',
      advice: `Increase assignment submission rate from ${studentData.submissionRate}% to above 90%. Use time management tools.`,
    })
  }

  if (studentData.participation < 60) {
    recommendations.push({
      icon: '💬',
      category: 'Participation',
      priority: 'Low',
      advice: `Increase class participation from ${studentData.participation}% to at least 70%. Ask questions and join group discussions.`,
    })
  }

  if (studentData.sleepHours < 6) {
    recommendations.push({
      icon: '😴',
      category: 'Health & Wellness',
      priority: 'Medium',
      advice: `Increase sleep from ${studentData.sleepHours} hours to 7-8 hours for better cognitive function and focus.`,
    })
  }

  if (recommendations.length === 0) {
    recommendations.push({
      icon: '🌟',
      category: 'Maintenance',
      priority: 'Low',
      advice: 'Great job! Keep maintaining your current academic habits. Consider peer tutoring to help others.',
    })
  }

  return recommendations
}

/**
 * Generate SHAP-like explanation summary
 */
export function generateExplanation(studentData, prediction) {
  const positiveFactors = []
  const negativeFactors = []

  if (studentData.attendance >= 80) positiveFactors.push(`✅ High attendance (${studentData.attendance}%)`)
  else if (studentData.attendance < 60) negativeFactors.push(`⚠️ Low attendance (${studentData.attendance}%)`)

  if (studentData.studyHours >= 6) positiveFactors.push(`✅ Strong study habits (${studentData.studyHours} hrs/day)`)
  else if (studentData.studyHours < 3) negativeFactors.push(`⚠️ Insufficient study time (${studentData.studyHours} hrs/day)`)

  if (studentData.gpa >= 7.5) positiveFactors.push(`✅ Strong academic foundation (GPA: ${studentData.gpa}/10)`)
  else if (studentData.gpa < 5) negativeFactors.push(`⚠️ Low GPA (${studentData.gpa}/10)`)

  if (studentData.backlogs === 0) positiveFactors.push('✅ No backlogs')
  else negativeFactors.push(`⚠️ ${studentData.backlogs} backlog(s) to address`)

  if (studentData.submissionRate >= 90) positiveFactors.push(`✅ Excellent submission rate (${studentData.submissionRate}%)`)
  else if (studentData.submissionRate < 60) negativeFactors.push(`⚠️ Low submission rate (${studentData.submissionRate}%)`)

  if (studentData.participation >= 75) positiveFactors.push(`✅ Active class participation (${studentData.participation}%)`)

  return {
    summary: `Based on the analysis of ${studentData.attendance}% attendance, ${studentData.studyHours} hours of daily study, ${studentData.gpa}/10 GPA, and other factors, the model predicts a ${prediction.percentage}% score (Grade ${prediction.grade}) with ${prediction.confidence}% confidence. ${prediction.status === 'Pass' ? 'The student is on track to pass.' : 'The student may need additional support to achieve passing marks.'}`,
    positiveFactors,
    negativeFactors,
    simpleExplanations: [
      `Attendance has a ${studentData.attendance >= 80 ? 'strong positive' : studentData.attendance >= 60 ? 'neutral' : 'significant negative'} impact on the prediction.`,
      `Study habits are ${studentData.studyHours >= 6 ? 'highly favorable' : studentData.studyHours >= 3 ? 'moderate' : 'concerning'} for academic success.`,
      `Previous academic performance (GPA: ${studentData.gpa}/10) ${studentData.gpa >= 7 ? 'strongly supports' : studentData.gpa >= 5 ? 'moderately supports' : 'weakens'} the prediction.`,
    ]
  }
}

