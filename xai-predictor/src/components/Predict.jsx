import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { runPrediction } from '../utils/predictionModel'
import { generateRecommendations, generateExplanation, getPercentageColor, getRiskColor } from '../utils/helpers'

const initialFormState = {
  studentName: '',
  attendance: 75,
  studyHours: 4,
  prevMarks: 65,
  internalMarks: 60,
  assignmentScore: 70,
  labScore: 65,
  backlogs: 2,
  gpa: 6.5,
  sleepHours: 7,
  internetAccess: 'Yes',
  extracurricular: 'Yes',
  participation: 55,
  submissionRate: 75,
}

export default function Predict({ addToHistory, lastPrediction, setCurrentPage }) {
  const [formData, setFormData] = useState(initialFormState)
  const [result, setResult] = useState(null)
  const [isCalculating, setIsCalculating] = useState(false)
  const [showResults, setShowResults] = useState(false)

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (result) setResult(null)
    if (showResults) setShowResults(false)
  }

  const handlePredict = () => {
    setIsCalculating(true)
    setShowResults(false)

    // Simulate API delay
    setTimeout(() => {
      const prediction = runPrediction(formData)
      setResult(prediction)
      addToHistory(formData, prediction)
      setIsCalculating(false)
      setShowResults(true)
    }, 800)
  }

  const recommendations = useMemo(() => {
    if (!result) return []
    return generateRecommendations(formData)
  }, [result, formData])

  const explanation = useMemo(() => {
    if (!result) return null
    return generateExplanation(formData, result)
  }, [result, formData])

  const CircularProgress = ({ percentage, size = 120, strokeWidth = 8 }) => {
    const radius = (size - strokeWidth) / 2
    const circumference = 2 * Math.PI * radius
    const offset = circumference - (percentage / 100) * circumference
    const color = getPercentageColor(percentage)

    return (
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(99,102,241,0.1)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          transform={`rotate(-90, ${size / 2}, ${size / 2})`}
        />
        <text
          x={size / 2}
          y={size / 2}
          textAnchor="middle"
          dominantBaseline="central"
          fill="#f1f5f9"
          fontSize="24"
          fontWeight="bold"
        >
          {percentage.toFixed(0)}%
        </text>
      </svg>
    )
  }

  const inputSections = [
    {
      title: '📊 Academic Parameters',
      fields: [
        { key: 'attendance', label: '📅 Attendance (%)', min: 0, max: 100, step: 1, unit: '%' },
        { key: 'studyHours', label: '⏰ Study Hours Per Day', min: 0.5, max: 12, step: 0.5, unit: 'hrs' },
        { key: 'prevMarks', label: '📄 Previous Marks (%)', min: 0, max: 100, step: 1, unit: '%' },
        { key: 'internalMarks', label: '📋 Internal Marks (%)', min: 0, max: 100, step: 1, unit: '%' },
        { key: 'assignmentScore', label: '📝 Assignment Score (%)', min: 0, max: 100, step: 1, unit: '%' },
        { key: 'labScore', label: '🔬 Lab Score (%)', min: 0, max: 100, step: 1, unit: '%' },
      ],
    },
    {
      title: '🎯 Behavioral & Personal Factors',
      fields: [
        { key: 'backlogs', label: '⚠️ Number of Backlogs', min: 0, max: 10, step: 1, unit: '' },
        { key: 'gpa', label: '🎓 Previous GPA (/10)', min: 0, max: 10, step: 0.1, unit: '/10' },
        { key: 'sleepHours', label: '😴 Sleep Hours', min: 4, max: 10, step: 0.5, unit: 'hrs' },
        { key: 'participation', label: '💬 Participation (%)', min: 0, max: 100, step: 1, unit: '%' },
        { key: 'submissionRate', label: '📤 Submission Rate (%)', min: 0, max: 100, step: 1, unit: '%' },
      ],
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="glass rounded-2xl p-6">
        <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
          <span>🎯</span> Predict Performance
        </h2>
        <p className="text-slate-400 mt-2">
          Enter student details below to get an instant, explainable performance prediction
        </p>
      </div>

      {/* Student Name Input */}
      <div className="glass-card mb-6">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
          👤 Student Information
        </h3>
        <div>
          <label className="block text-sm text-slate-300 mb-2">👤 Student Name</label>
          <input
            type="text"
            placeholder="e.g., John Doe"
            value={formData.studentName}
            onChange={(e) => handleChange('studentName', e.target.value)}
            className="input-field"
          />
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="space-y-6">
          {inputSections.map((section) => (
            <div key={section.title} className="glass-card">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-5">
                {section.title}
              </h3>
              <div className="space-y-5">
                {section.fields.map((field) => (
                  <div key={field.key}>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm text-slate-300">{field.label}</label>
                      <span className="text-sm font-semibold text-indigo-400">
                        {formData[field.key]} {field.unit}
                      </span>
                    </div>
                    <input
                      type="range"
                      min={field.min}
                      max={field.max}
                      step={field.step}
                      value={formData[field.key]}
                      onChange={(e) => handleChange(field.key, parseFloat(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-slate-600 mt-1">
                      <span>{field.min}</span>
                      <span>{field.max}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Internet & Extracurricular */}
          <div className="glass-card">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-5">
              🌐 Additional Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-slate-300 mb-2">🌐 Internet Access</label>
                <select
                  value={formData.internetAccess}
                  onChange={(e) => handleChange('internetAccess', e.target.value)}
                  className="input-field"
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-2">🎨 Extracurricular</label>
                <select
                  value={formData.extracurricular}
                  onChange={(e) => handleChange('extracurricular', e.target.value)}
                  className="input-field"
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
            </div>
          </div>

          {/* Predict Button */}
          <motion.button
            onClick={handlePredict}
            disabled={isCalculating}
            className="btn-primary w-full text-lg py-4 flex items-center justify-center gap-3"
            whileHover={{ scale: isCalculating ? 1 : 1.01 }}
            whileTap={{ scale: isCalculating ? 1 : 0.99 }}
          >
            {isCalculating ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Analyzing...
              </>
            ) : (
              <>🎯 Predict Performance</>
            )}
          </motion.button>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          <AnimatePresence mode="wait">
            {!showResults && !isCalculating ? (
              <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="glass-card flex flex-col items-center justify-center min-h-[400px] text-center"
              >
                <div className="w-20 h-20 rounded-full bg-indigo-500/10 flex items-center justify-center mb-5">
                  <span className="text-4xl">🎯</span>
                </div>
                <h3 className="text-xl font-semibold text-slate-100 mb-3">Ready to Predict</h3>
                <p className="text-slate-400 max-w-sm">
                  Fill in the student details on the left and click <strong className="text-slate-200">Predict Performance</strong>.
                </p>
              </motion.div>
            ) : isCalculating ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="glass-card flex flex-col items-center justify-center min-h-[400px]"
              >
                <div className="w-16 h-16 rounded-full border-4 border-indigo-500/30 border-t-indigo-500 animate-spin mb-5" />
                <p className="text-slate-400 animate-pulse">Analyzing student data with ML model...</p>
              </motion.div>
            ) : result ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                {/* Main Prediction Result */}
                <div className="glass-card">
                  <h3 className="text-lg font-bold text-slate-100 mb-6 flex items-center gap-2">
                    <span>🎯</span> Prediction Result
                  </h3>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    {/* Circular Progress */}
                    <div className="flex flex-col items-center justify-center p-4 bg-navy-800/30 rounded-xl">
                      <p className="text-xs text-slate-400 mb-3">Predicted Percentage</p>
                      <CircularProgress percentage={result.percentage} />
                    </div>

                    {/* Grade */}
                    <div className="flex flex-col items-center justify-center p-4 bg-navy-800/30 rounded-xl">
                      <p className="text-xs text-slate-400 mb-2">Grade</p>
                      <p
                        className="text-5xl font-extrabold mb-1"
                        style={{ color: result.performanceColor }}
                      >
                        {result.grade}
                      </p>
                      <p className="text-sm text-slate-300">{result.performanceLevel}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {/* Confidence */}
                    <div className="p-4 bg-navy-800/30 rounded-xl text-center">
                      <p className="text-xs text-slate-400 mb-1">Confidence</p>
                      <p className="text-2xl font-bold text-indigo-400">{result.confidence}%</p>
                      <span className={result.status === 'Pass' ? 'badge-pass mt-2' : 'badge-fail mt-2'}>
                        {result.status === 'Pass' ? '✅ Pass' : '❌ Fail'}
                      </span>
                    </div>

                    {/* Risk Level */}
                    <div className="p-4 bg-navy-800/30 rounded-xl text-center">
                      <p className="text-xs text-slate-400 mb-1">Risk Level</p>
                      <p
                        className="text-2xl font-bold"
                        style={{ color: getRiskColor(result.riskLevel) }}
                      >
                        {result.riskLevel}
                      </p>
                      <span className="text-xs text-slate-400 mt-1">
                        {result.riskLevel === 'Low' ? '✅ On Track' : result.riskLevel === 'Medium' ? '⚠️ Needs Attention' : '🔴 Critical'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Probability Distribution */}
                <div className="glass-card">
                  <h4 className="text-sm font-semibold text-slate-400 mb-4">📊 Probability Distribution</h4>
                  <div className="space-y-3">
                    {result.probabilities.map((prob) => (
                      <div key={prob.category} className="flex items-center gap-3">
                        <span className="text-sm text-slate-300 w-20">{prob.category}</span>
                        <div className="flex-1 h-5 rounded-full bg-navy-800/60 overflow-hidden">
                          <motion.div
                            className="h-full rounded-full"
                            style={{
                              background: prob.category === 'Excellent' ? '#10b981' :
                                prob.category === 'Good' ? '#6366f1' :
                                prob.category === 'Average' ? '#f59e0b' : '#f43f5e',
                            }}
                            initial={{ width: 0 }}
                            animate={{ width: `${prob.probability}%` }}
                            transition={{ duration: 1, delay: 0.3 }}
                          />
                        </div>
                        <span className="text-sm text-slate-400 w-14 text-right">{prob.probability}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Performance Gauge */}
                <div className="glass-card">
                  <h4 className="text-sm font-semibold text-slate-400 mb-4">🎯 Performance Gauge</h4>
                  <div className="flex justify-center">
                    <CircularProgress percentage={result.percentage} size={160} strokeWidth={10} />
                  </div>
                </div>

                {/* Explanation */}
                {explanation && (
                  <div className="glass-card">
                    <h4 className="text-sm font-semibold text-slate-400 mb-4">🔍 AI Explanation</h4>
                    <div className="bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-4 mb-4">
                      <p className="text-sm text-slate-300 leading-relaxed">{explanation.summary}</p>
                    </div>
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs font-semibold text-emerald-400 mb-2">✅ Positive Factors</p>
                        <ul className="space-y-1.5">
                          {explanation.positiveFactors.map((f, i) => (
                            <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                              <span className="text-emerald-400 mt-0.5">•</span>
                              {f.replace('✅ ', '')}
                            </li>
                          ))}
                          {explanation.positiveFactors.length === 0 && (
                            <li className="text-xs text-slate-500">No significant positive factors identified</li>
                          )}
                        </ul>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-amber-400 mb-2">⚠️ Areas of Concern</p>
                        <ul className="space-y-1.5">
                          {explanation.negativeFactors.map((f, i) => (
                            <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                              <span className="text-amber-400 mt-0.5">•</span>
                              {f.replace('⚠️ ', '')}
                            </li>
                          ))}
                          {explanation.negativeFactors.length === 0 && (
                            <li className="text-xs text-slate-500">No significant concerns identified</li>
                          )}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                <div className="glass-card">
                  <h4 className="text-sm font-semibold text-slate-400 mb-4">💡 Personalized Recommendations</h4>
                  <div className="space-y-3">
                    {recommendations.map((rec, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-xl bg-navy-800/30 border-l-4"
                        style={{
                          borderLeftColor:
                            rec.priority === 'High' ? '#f43f5e' :
                            rec.priority === 'Medium' ? '#f59e0b' : '#10b981',
                        }}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span>{rec.icon}</span>
                          <span className="text-sm font-medium text-slate-200">{rec.category}</span>
                          <span
                            className="text-xs px-2 py-0.5 rounded-full font-medium"
                            style={{
                              background:
                                rec.priority === 'High' ? 'rgba(244,63,94,0.15)' :
                                rec.priority === 'Medium' ? 'rgba(245,158,11,0.15)' : 'rgba(16,185,129,0.15)',
                              color:
                                rec.priority === 'High' ? '#f43f5e' :
                                rec.priority === 'Medium' ? '#f59e0b' : '#10b981',
                            }}
                          >
                            {rec.priority}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 ml-7">{rec.advice}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4">
                  <button
                    onClick={() => setCurrentPage('history')}
                    className="btn-secondary flex-1"
                  >
                    📋 View History
                  </button>
                  <button
                    onClick={() => setCurrentPage('xai')}
                    className="btn-primary flex-1"
                  >
                    🔍 Detailed XAI
                  </button>
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

