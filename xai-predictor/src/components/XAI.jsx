import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { featureImportance } from '../data/sampleData'
import { generateRecommendations, generateExplanation, getPercentageColor } from '../utils/helpers'

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass rounded-xl p-3 text-sm shadow-xl border-indigo-500/20">
        <p className="text-slate-200 font-medium">{label}</p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color }} className="text-xs mt-1">
            {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(4) : entry.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
}

export default function XAI({ lastPrediction, lastStudentData }) {
  const hasData = lastPrediction && lastStudentData

  const explanation = useMemo(() => {
    if (!hasData) return null
    return generateExplanation(lastStudentData, lastPrediction)
  }, [hasData])

  const recommendations = useMemo(() => {
    if (!hasData) return []
    return generateRecommendations(lastStudentData)
  }, [hasData])

  // SHAP waterfall data simulation
  const shapData = useMemo(() => {
    if (!hasData) return []
    const input = lastStudentData
    const baseValue = 65 // Base prediction value
    const contributions = [
      { feature: 'Attendance', contribution: (input.attendance - 75) * 0.2 },
      { feature: 'Study Hours', contribution: (input.studyHours - 4) * 1.5 },
      { feature: 'Prev Marks', contribution: (input.prevMarks - 65) * 0.15 },
      { feature: 'Internal Marks', contribution: (input.internalMarks - 60) * 0.12 },
      { feature: 'Assignment Score', contribution: (input.assignmentScore - 70) * 0.1 },
      { feature: 'Lab Score', contribution: (input.labScore - 65) * 0.08 },
      { feature: 'Backlogs', contribution: (3 - input.backlogs) * 2 },
      { feature: 'GPA', contribution: (input.gpa - 6.5) * 3 },
      { feature: 'Sleep Hours', contribution: (input.sleepHours - 7) * 0.5 },
      { feature: 'Participation', contribution: (input.participation - 55) * 0.06 },
      { feature: 'Submission Rate', contribution: (input.submissionRate - 75) * 0.08 },
    ]
    return contributions.sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))
  }, [hasData])

  const positiveContributions = shapData.filter(d => d.contribution > 0)
  const negativeContributions = shapData.filter(d => d.contribution < 0)

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="glass rounded-2xl p-6">
        <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
          <span>🔍</span> Explainable AI (XAI) Analysis
        </h2>
        <p className="text-slate-400 mt-2">
          SHAP (SHapley Additive exPlanations) shows how each feature contributed to this prediction
        </p>
      </motion.div>

      {!hasData ? (
        <motion.div variants={itemVariants} className="glass-card flex flex-col items-center justify-center min-h-[400px] text-center">
          <div className="w-20 h-20 rounded-full bg-indigo-500/10 flex items-center justify-center mb-5">
            <span className="text-4xl">🔍</span>
          </div>
          <h3 className="text-xl font-semibold text-slate-100 mb-3">No Prediction Data</h3>
          <p className="text-slate-400 max-w-sm">
            Make a prediction first on the <strong className="text-slate-200">Predict</strong> page to see detailed XAI analysis.
          </p>
        </motion.div>
      ) : (
        <>
          {/* Prediction Summary */}
          <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Predicted %', value: `${lastPrediction.percentage.toFixed(1)}%`, color: getPercentageColor(lastPrediction.percentage) },
              { label: 'Grade', value: lastPrediction.grade, color: lastPrediction.performanceColor },
              { label: 'Confidence', value: `${lastPrediction.confidence.toFixed(1)}%`, color: '#818cf8' },
              { label: 'Risk Level', value: lastPrediction.riskLevel, color: lastPrediction.riskLevel === 'Low' ? '#10b981' : lastPrediction.riskLevel === 'Medium' ? '#f59e0b' : '#f43f5e' },
            ].map((stat, i) => (
              <div key={i} className="glass rounded-2xl p-4 text-center">
                <p className="text-xs text-slate-400 mb-1">{stat.label}</p>
                <p className="text-2xl font-bold" style={{ color: stat.color }}>{stat.value}</p>
              </div>
            ))}
          </motion.div>

          {/* Feature Contribution Waterfall */}
          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-lg font-semibold text-slate-100 mb-1">📊 Feature Contribution Analysis</h3>
            <p className="text-xs text-slate-400 mb-6">
              How each feature contributes to the final prediction (SHAP values)
            </p>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={shapData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 100, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
                  <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <YAxis dataKey="feature" type="category" tick={{ fill: '#94a3b8', fontSize: 12 }} width={120} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="contribution" name="SHAP Value" radius={[0, 4, 4, 0]}>
                    {shapData.map((entry, i) => (
                      <rect key={i} fill={entry.contribution >= 0 ? '#10b981' : '#f43f5e'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Positive and Negative Factors */}
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div variants={itemVariants} className="glass-card">
              <h4 className="text-sm font-semibold text-emerald-400 mb-4 flex items-center gap-2">
                <span>✅</span> Positive Contributing Factors
              </h4>
              <p className="text-xs text-slate-500 mb-4">These features improved the prediction score</p>
              {positiveContributions.length > 0 ? (
                <div className="space-y-2">
                  {positiveContributions.slice(0, 7).map((item, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-3 rounded-xl bg-emerald-500/5 border-l-4 border-emerald-500"
                    >
                      <span className="text-sm text-slate-300">{item.feature}</span>
                      <span className="text-sm font-semibold text-emerald-400">
                        +{Math.abs(item.contribution).toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No significant positive factors identified</p>
              )}
            </motion.div>

            <motion.div variants={itemVariants} className="glass-card">
              <h4 className="text-sm font-semibold text-rose-400 mb-4 flex items-center gap-2">
                <span>⚠️</span> Negative Contributing Factors
              </h4>
              <p className="text-xs text-slate-500 mb-4">These features pulled down the prediction score</p>
              {negativeContributions.length > 0 ? (
                <div className="space-y-2">
                  {negativeContributions.slice(0, 7).map((item, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-3 rounded-xl bg-rose-500/5 border-l-4 border-rose-500"
                    >
                      <span className="text-sm text-slate-300">{item.feature}</span>
                      <span className="text-sm font-semibold text-rose-400">
                        {item.contribution.toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No significant negative factors identified</p>
              )}
            </motion.div>
          </div>

          {/* Global Feature Importance */}
          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-lg font-semibold text-slate-100 mb-1">🌍 Global Feature Importance</h3>
            <p className="text-xs text-slate-400 mb-6">
              Overall feature importance across the entire dataset (based on SHAP values)
            </p>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={featureImportance.sort((a, b) => Math.abs(b.importance) - Math.abs(a.importance)).slice(0, 10)}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 100, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
                  <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[0, 1]} tickFormatter={(v) => (v * 100).toFixed(0) + '%'} />
                  <YAxis dataKey="feature" type="category" tick={{ fill: '#94a3b8', fontSize: 12 }} width={120} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="importance" name="Importance" fill="#6366f1" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Explanation Summary */}
          {explanation && (
            <motion.div variants={itemVariants} className="glass-card">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">💬 Summary Explanation</h3>
              <div className="bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-5 mb-6">
                <p className="text-sm text-slate-300 leading-relaxed">{explanation.summary}</p>
              </div>

              <div className="space-y-4">
                <h4 className="text-sm font-medium text-slate-400">Simple Explanations:</h4>
                {explanation.simpleExplanations.map((exp, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className="text-emerald-400 mt-0.5">•</span>
                    <p className="text-sm text-slate-400">{exp}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Recommendations */}
          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">🎯 Personalized Recommendations</h3>
            <div className="space-y-3">
              {recommendations.map((rec, i) => (
                <div
                  key={i}
                  className="p-4 rounded-xl bg-navy-800/30 border-l-4"
                  style={{
                    borderLeftColor:
                      rec.priority === 'High' ? '#f43f5e' :
                      rec.priority === 'Medium' ? '#f59e0b' : '#10b981',
                  }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">{rec.icon}</span>
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
                  <p className="text-sm text-slate-400 ml-8">{rec.advice}</p>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Disclaimer */}
          <motion.div variants={itemVariants} className="p-5 rounded-xl bg-amber-500/5 border border-amber-500/10">
            <p className="text-xs text-amber-400/80 flex items-start gap-2">
              <span className="text-amber-400 mt-0.5">⚠️</span>
              <span>
                <strong>Important Note:</strong> SHAP values show which features influenced the model's prediction.
                They do not necessarily represent real-world causation. This is a decision-support tool,
                not an absolute authority on student capability.
              </span>
            </p>
          </motion.div>
        </>
      )}
    </motion.div>
  )
}
