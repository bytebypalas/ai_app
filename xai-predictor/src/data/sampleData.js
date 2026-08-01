/**
 * Sample student data for the EduPredict AI dashboard.
 * Used for analytics visualizations and demonstration purposes.
 */

export const performanceDistribution = [
  { category: 'Poor', count: 85, color: '#f43f5e' },
  { category: 'Average', count: 210, color: '#f59e0b' },
  { category: 'Good', count: 320, color: '#6366f1' },
  { category: 'Excellent', count: 185, color: '#10b981' },
]

export const featureImportance = [
  { feature: 'Attendance', importance: 0.92 },
  { feature: 'Study Hours', importance: 0.88 },
  { feature: 'Internal Marks', importance: 0.85 },
  { feature: 'Previous GPA', importance: 0.81 },
  { feature: 'Assignment Score', importance: 0.78 },
  { feature: 'Lab Score', importance: 0.72 },
  { feature: 'Submission Rate', importance: 0.68 },
  { feature: 'Participation', importance: 0.65 },
  { feature: 'Previous Marks', importance: 0.61 },
  { feature: 'Sleep Hours', importance: 0.45 },
  { feature: 'Backlogs', importance: -0.55 },
  { feature: 'Extracurricular', importance: 0.32 },
]

export const attendanceVsPerformance = Array.from({ length: 200 }, (_, i) => ({
  attendance: Math.random() * 40 + 60,
  score: Math.random() * 30 + 60 + (Math.random() > 0.5 ? 10 : 0),
  category: ['Poor', 'Average', 'Good', 'Excellent'][Math.floor(Math.random() * 4)],
}))

export const studyHoursDistribution = [
  { category: 'Poor', min: 1.5, q1: 2.5, median: 3.5, q3: 4.5, max: 6.5 },
  { category: 'Average', min: 2.0, q1: 3.5, median: 5.0, q3: 6.5, max: 8.0 },
  { category: 'Good', min: 3.0, q1: 5.0, median: 6.5, q3: 8.0, max: 10.0 },
  { category: 'Excellent', min: 4.0, q1: 6.0, median: 7.5, q3: 9.0, max: 12.0 },
]

export const correlationData = [
  { feature1: 'Attendance', feature2: 'Performance', correlation: 0.85 },
  { feature1: 'Study Hours', feature2: 'Performance', correlation: 0.78 },
  { feature1: 'GPA', feature2: 'Performance', correlation: 0.82 },
  { feature1: 'Backlogs', feature2: 'Performance', correlation: -0.72 },
  { feature1: 'Participation', feature2: 'Performance', correlation: 0.64 },
  { feature1: 'Sleep Hours', feature2: 'Performance', correlation: 0.42 },
  { feature1: 'Attendance', feature2: 'Study Hours', correlation: 0.45 },
  { feature1: 'Attendance', feature2: 'GPA', correlation: 0.68 },
  { feature1: 'Study Hours', feature2: 'GPA', correlation: 0.71 },
  { feature1: 'Backlogs', feature2: 'Attendance', correlation: -0.55 },
  { feature1: 'Backlogs', feature2: 'Study Hours', correlation: -0.48 },
  { feature1: 'Participation', feature2: 'Attendance', correlation: 0.52 },
]

export const modelComparison = [
  { model: 'Logistic Regression', accuracy: 0.842, precision: 0.831, recall: 0.842, f1: 0.836 },
  { model: 'Decision Tree', accuracy: 0.871, precision: 0.865, recall: 0.871, f1: 0.868 },
  { model: 'Random Forest', accuracy: 0.942, precision: 0.938, recall: 0.942, f1: 0.940 },
  { model: 'XGBoost', accuracy: 0.938, precision: 0.935, recall: 0.938, f1: 0.936 },
]

export const gradeScale = [
  { min: 90, max: 100, grade: 'A+', description: 'Outstanding' },
  { min: 80, max: 89, grade: 'A', description: 'Excellent' },
  { min: 70, max: 79, grade: 'B+', description: 'Very Good' },
  { min: 60, max: 69, grade: 'B', description: 'Good' },
  { min: 50, max: 59, grade: 'C', description: 'Average' },
  { min: 0, max: 49, grade: 'F', description: 'Fail' },
]

export const performanceLevels = [
  { min: 85, max: 100, level: 'Excellent', color: '#10b981' },
  { min: 70, max: 84, level: 'Good', color: '#6366f1' },
  { min: 55, max: 69, level: 'Above Average', color: '#06b6d4' },
  { min: 40, max: 54, level: 'Average', color: '#f59e0b' },
  { min: 0, max: 39, level: 'Poor', color: '#f43f5e' },
]

export const samplePredictions = [
  { id: 1, date: '2024-12-15 10:30', attendance: 92, studyHours: 6.5, prevMarks: 85, grade: 'A+', percentage: 94.2, confidence: 96, risk: 'Low', status: 'Pass' },
  { id: 2, date: '2024-12-14 14:20', attendance: 78, studyHours: 4.0, prevMarks: 72, grade: 'B+', percentage: 76.8, confidence: 88, risk: 'Low', status: 'Pass' },
  { id: 3, date: '2024-12-13 09:15', attendance: 55, studyHours: 2.5, prevMarks: 48, grade: 'C', percentage: 52.3, confidence: 82, risk: 'Medium', status: 'Pass' },
  { id: 4, date: '2024-12-12 16:45', attendance: 35, studyHours: 1.5, prevMarks: 38, grade: 'F', percentage: 32.1, confidence: 91, risk: 'High', status: 'Fail' },
  { id: 5, date: '2024-12-11 11:00', attendance: 88, studyHours: 5.5, prevMarks: 78, grade: 'A', percentage: 85.6, confidence: 93, risk: 'Low', status: 'Pass' },
]

