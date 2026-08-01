import React from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, ScatterChart, Scatter, ZAxis,
  LineChart, Line, Legend,
} from 'recharts'
import {
  performanceDistribution, featureImportance, attendanceVsPerformance,
  studyHoursDistribution, modelComparison,
} from '../data/sampleData'

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass rounded-xl p-3 text-sm shadow-xl border-indigo-500/20">
        <p className="text-slate-200 font-medium">{label || payload[0].name}</p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color }} className="text-xs mt-1">
            {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

const COLORS = {
  Poor: '#f43f5e',
  Average: '#f59e0b',
  Good: '#6366f1',
  Excellent: '#10b981',
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

function ChartCard({ title, subtitle, children, delay = 0 }) {
  return (
    <motion.div
      variants={itemVariants}
      className="glass-card"
    >
      <h3 className="text-lg font-semibold text-slate-100 mb-1">{title}</h3>
      {subtitle && <p className="text-xs text-slate-400 mb-4">{subtitle}</p>}
      <div className="h-[350px]">
        {children}
      </div>
    </motion.div>
  )
}

export default function Analytics() {
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
          <span>📊</span> Analytics Dashboard
        </h2>
        <p className="text-slate-400 mt-2">
          Comprehensive insights and visualizations from student performance data
        </p>
      </motion.div>

      {/* Summary Stats */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Students', value: '1,200+', change: '+12%', color: 'from-indigo-500 to-purple-600' },
          { label: 'Avg Attendance', value: '74.3%', change: '+3.2%', color: 'from-emerald-500 to-teal-500' },
          { label: 'Avg Study Hours', value: '5.2 hrs', change: '+0.8', color: 'from-cyan-500 to-blue-600' },
          { label: 'Avg GPA', value: '6.8/10', change: '+0.3', color: 'from-amber-500 to-orange-500' },
        ].map((stat, i) => (
          <div key={i} className="glass rounded-2xl p-5 text-center">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center mx-auto mb-3`}>
              <span className="text-white text-sm font-bold">●</span>
            </div>
            <p className="text-2xl font-bold text-slate-100">{stat.value}</p>
            <p className="text-xs text-slate-400 mt-1">{stat.label}</p>
            <p className="text-xs text-emerald-400 mt-0.5">{stat.change}</p>
          </div>
        ))}
      </motion.div>

      {/* Performance Distribution */}
      <div className="grid md:grid-cols-2 gap-6">
        <ChartCard title="📊 Performance Distribution" subtitle="Distribution of students across performance categories">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={performanceDistribution} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
              <XAxis dataKey="category" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" name="Students" radius={[8, 8, 0, 0]}>
                {performanceDistribution.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="🥧 Performance Breakdown" subtitle="Proportion of students by category">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={performanceDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
                dataKey="count"
                nameKey="category"
              >
                {performanceDistribution.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Feature Importance */}
      <ChartCard title="⭐ Feature Importance" subtitle="Top features influencing student performance predictions">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={featureImportance.sort((a, b) => Math.abs(b.importance) - Math.abs(a.importance)).slice(0, 8)}
            layout="vertical"
            margin={{ top: 10, right: 30, left: 100, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
            <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[-1, 1]} />
            <YAxis dataKey="feature" type="category" tick={{ fill: '#94a3b8', fontSize: 12 }} width={120} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="importance" name="Importance" radius={[0, 4, 4, 0]}>
              {featureImportance.map((entry, i) => (
                <Cell key={i} fill={entry.importance >= 0 ? '#6366f1' : '#f43f5e'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Attendance vs Performance Scatter */}
      <ChartCard title="📈 Attendance vs Performance" subtitle="Relationship between attendance and academic scores">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
            <XAxis dataKey="attendance" name="Attendance %" tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[50, 100]} />
            <YAxis dataKey="score" name="Score %" tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[50, 100]} />
            <ZAxis range={[60, 60]} />
            <Tooltip content={<CustomTooltip />} />
            <Scatter
              data={attendanceVsPerformance}
              fill="#6366f1"
              opacity={0.5}
              name="Students"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Study Hours Distribution */}
      <ChartCard title="⏰ Study Hours by Performance" subtitle="Distribution of study hours across performance levels">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={studyHoursDistribution}
            margin={{ top: 10, right: 10, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
            <XAxis dataKey="category" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="min" name="Min" stackId="a" fill="rgba(99,102,241,0.2)" />
            <Bar dataKey="q1" name="Q1" stackId="a" fill="rgba(99,102,241,0.4)" />
            <Bar dataKey="median" name="Median" stackId="a" fill="#6366f1" />
            <Bar dataKey="q3" name="Q3" stackId="a" fill="rgba(99,102,241,0.7)" />
            <Bar dataKey="max" name="Max" stackId="a" fill="rgba(99,102,241,0.9)" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Model Comparison */}
      <ChartCard title="🤖 Model Performance Comparison" subtitle="Accuracy comparison across different ML models">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={modelComparison}
            margin={{ top: 10, right: 10, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
            <XAxis dataKey="model" tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[0.8, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{value}</span>} />
            <Bar dataKey="accuracy" name="Accuracy" fill="#6366f1" radius={[4, 4, 0, 0]} />
            <Bar dataKey="precision" name="Precision" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="recall" name="Recall" fill="#06b6d4" radius={[4, 4, 0, 0]} />
            <Bar dataKey="f1" name="F1 Score" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Key Insights */}
      <motion.div variants={itemVariants} className="glass-card">
        <h3 className="text-lg font-semibold text-slate-100 mb-4">💡 Key Insights</h3>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            {
              icon: '📅',
              title: 'Attendance Matters Most',
              desc: 'Attendance has the highest correlation with academic performance. Students with >80% attendance consistently perform better.',
            },
            {
              icon: '⏰',
              title: 'Study Habits Matter',
              desc: 'Students studying 6+ hours per day show significantly better performance. Consistency matters more than intensity.',
            },
            {
              icon: '🎯',
              title: 'Random Forest Best',
              desc: 'Random Forest achieved 94.2% accuracy, making it the best performing model for this dataset.',
            },
          ].map((insight, i) => (
            <div key={i} className="p-4 rounded-xl bg-navy-800/30">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{insight.icon}</span>
                <h4 className="text-sm font-semibold text-slate-200">{insight.title}</h4>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{insight.desc}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  )
}

