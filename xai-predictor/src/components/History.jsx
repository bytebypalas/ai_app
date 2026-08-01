import React, { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { getRiskColor, getRiskBadge, getStatusBadge } from '../utils/helpers'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } }
}

export default function History({ predictionHistory, clearHistory }) {
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('newest')

  const filteredHistory = useMemo(() => {
    let data = [...predictionHistory]

    // Search filter
    if (search) {
      const term = search.toLowerCase()
      data = data.filter(item =>
        (item.grade && item.grade.toLowerCase().includes(term)) ||
        (item.performanceLevel && item.performanceLevel.toLowerCase().includes(term)) ||
        (item.riskLevel && item.riskLevel.toLowerCase().includes(term)) ||
        (item.status && item.status.toLowerCase().includes(term))
      )
    }

    // Sort
    switch (sortBy) {
      case 'newest':
        data.sort((a, b) => new Date(b.date) - new Date(a.date))
        break
      case 'oldest':
        data.sort((a, b) => new Date(a.date) - new Date(b.date))
        break
      case 'highest':
        data.sort((a, b) => b.percentage - a.percentage)
        break
      case 'lowest':
        data.sort((a, b) => a.percentage - b.percentage)
        break
      default:
        break
    }

    return data
  }, [predictionHistory, search, sortBy])

  const exportCSV = () => {
    if (predictionHistory.length === 0) return

const headers = ['Date', 'Student Name', 'Grade', 'Score %', 'Performance', 'Confidence', 'Risk', 'Status']
    const csvContent = [
      headers.join(','),
      ...predictionHistory.map(item =>
        [
          item.date,
          `"${item.studentName || 'Unnamed Student'}"`,
          item.grade,
          item.percentage.toFixed(1),
          item.performanceLevel,
          item.confidence.toFixed(1),
          item.riskLevel,
          item.status,
        ].join(',')
      ),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'edupredict_history.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

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
          <span>📋</span> Prediction History
        </h2>
        <p className="text-slate-400 mt-2">
          View and manage your prediction records
        </p>
      </motion.div>

      {predictionHistory.length === 0 ? (
        <motion.div variants={itemVariants} className="glass-card flex flex-col items-center justify-center min-h-[400px] text-center">
          <div className="w-20 h-20 rounded-full bg-indigo-500/10 flex items-center justify-center mb-5">
            <span className="text-4xl">📋</span>
          </div>
          <h3 className="text-xl font-semibold text-slate-100 mb-3">No Predictions Yet</h3>
          <p className="text-slate-400 max-w-sm">
            Make your first prediction on the <strong className="text-slate-200">Predict</strong> page to start building your history.
          </p>
        </motion.div>
      ) : (
        <>
          {/* Controls */}
          <motion.div variants={itemVariants} className="glass-card">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    type="text"
                    placeholder="Search by grade, performance, risk..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="input-field pl-10"
                  />
                </div>
              </div>
              <div className="w-full sm:w-48">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="input-field"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="highest">Highest %</option>
                  <option value="lowest">Lowest %</option>
                </select>
              </div>
              <button
                onClick={clearHistory}
                className="btn-secondary whitespace-nowrap"
              >
                🗑️ Clear All
              </button>
            </div>
          </motion.div>

          {/* Stats Summary */}
          <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Predictions', value: predictionHistory.length, color: '#818cf8' },
              { label: 'Average Score', value: `${(predictionHistory.reduce((sum, p) => sum + p.percentage, 0) / predictionHistory.length).toFixed(1)}%`, color: '#10b981' },
              { label: 'Pass Rate', value: `${((predictionHistory.filter(p => p.status === 'Pass').length / predictionHistory.length) * 100).toFixed(0)}%`, color: '#06b6d4' },
              { label: 'High Risk', value: predictionHistory.filter(p => p.riskLevel === 'High').length, color: '#f43f5e' },
            ].map((stat, i) => (
              <div key={i} className="glass rounded-2xl p-4 text-center">
                <p className="text-xs text-slate-400 mb-1">{stat.label}</p>
                <p className="text-2xl font-bold" style={{ color: stat.color }}>{stat.value}</p>
              </div>
            ))}
          </motion.div>

          {/* History Table */}
          <motion.div variants={itemVariants} className="glass-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-indigo-500/10">
<th className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider py-3 px-4">Date</th>
                    <th className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider py-3 px-4">Student</th>
                    <th className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider py-3 px-4">Grade</th>
                    <th className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider py-3 px-4">Score %</th>
                    <th className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider py-3 px-4 hidden md:table-cell">Performance</th>
                    <th className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider py-3 px-4 hidden md:table-cell">Confidence</th>
                    <th className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider py-3 px-4">Risk</th>
                    <th className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider py-3 px-4">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.map((item, i) => (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.03 }}
                      className="border-b border-indigo-500/5 hover:bg-indigo-500/5 transition-colors"
                    >
<td className="py-3 px-4 text-sm text-slate-300 whitespace-nowrap">{item.date}</td>
                      <td className="py-3 px-4 text-sm text-slate-300">{item.studentName || 'Unnamed Student'}</td>
                      <td className="py-3 px-4">
                        <span
                          className="text-sm font-bold"
                          style={{ color: item.performanceColor || '#6366f1' }}
                        >
                          {item.grade}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-300 font-medium">{item.percentage.toFixed(1)}%</td>
                      <td className="py-3 px-4 text-sm text-slate-400 hidden md:table-cell">{item.performanceLevel}</td>
                      <td className="py-3 px-4 text-sm text-slate-400 hidden md:table-cell">{item.confidence.toFixed(1)}%</td>
                      <td className="py-3 px-4">
                        <span
                          className="text-xs px-2 py-1 rounded-full font-medium"
                          style={{
                            background: `${getRiskColor(item.riskLevel)}15`,
                            color: getRiskColor(item.riskLevel),
                          }}
                        >
                          {item.riskLevel}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={item.status === 'Pass' ? 'badge-pass' : 'badge-fail'}>
                          {item.status === 'Pass' ? '✅' : '❌'} {item.status}
                        </span>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            {filteredHistory.length === 0 && (
              <div className="text-center py-8 text-slate-500 text-sm">
                No records match your search.
              </div>
            )}
          </motion.div>

          {/* Export */}
          <motion.div variants={itemVariants} className="glass-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-300 font-medium">📤 Export Options</p>
              <p className="text-xs text-slate-500">Download your prediction history as CSV</p>
            </div>
            <button onClick={exportCSV} className="btn-primary">
              📥 Download CSV
            </button>
          </motion.div>
        </>
      )}
    </motion.div>
  )
}
