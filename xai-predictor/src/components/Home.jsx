import React, { useEffect, useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import { performanceDistribution } from '../data/sampleData'
import { formatNumber } from '../utils/helpers'

/* ===== Unique SVG Icons for Stats ===== */
const StatIcons = {
  students: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
      <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
      <path d="M6 12v5c3 3 9 3 12 0v-5" />
      <path d="M22 10v6" />
    </svg>
  ),
  accuracy: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
      <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
      <path d="M12 6v6l4 2" />
      <circle cx="12" cy="12" r="1" fill="currentColor" />
    </svg>
  ),
  features: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <rect x="9" y="9" width="6" height="6" rx="1" />
      <path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3" />
    </svg>
  ),
  predictions: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
      <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
      <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
      <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
      <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
    </svg>
  ),
}

const gradientMap = {
  'from-indigo-500 to-purple-600': { from: '#6366f1', to: '#a855f7', glow: 'rgba(99,102,241,0.4)' },
  'from-emerald-500 to-teal-500': { from: '#10b981', to: '#14b8a6', glow: 'rgba(16,185,129,0.4)' },
  'from-cyan-500 to-blue-600': { from: '#06b6d4', to: '#2563eb', glow: 'rgba(6,182,212,0.4)' },
  'from-amber-500 to-orange-500': { from: '#f59e0b', to: '#f97316', glow: 'rgba(245,158,11,0.4)' },
}

const stats = [
  { key: 'students', label: 'Students Analyzed', value: 1200, suffix: '+', change: '+12%', trend: 'up', gradient: 'from-indigo-500 to-purple-600', icon: StatIcons.students },
  { key: 'accuracy', label: 'Model Accuracy', value: 94.2, suffix: '%', decimals: 1, change: '+5.2%', trend: 'up', gradient: 'from-emerald-500 to-teal-500', icon: StatIcons.accuracy },
  { key: 'features', label: 'Features Analyzed', value: 14, suffix: '+', change: '+3', trend: 'up', gradient: 'from-cyan-500 to-blue-600', icon: StatIcons.features },
  { key: 'predictions', label: 'Predictions Made', value: 5800, suffix: '+', change: '+18%', trend: 'up', gradient: 'from-amber-500 to-orange-500', icon: StatIcons.predictions },
]

/** Animated count-up number using requestAnimationFrame */
function AnimatedNumber({ value, decimals = 0, suffix = '' }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    if (!inView) return
    let raf
    const duration = 1600
    const start = performance.now()
    const tick = (now) => {
      const p = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - p, 3)
      setDisplay(value * eased)
      if (p < 1) raf = requestAnimationFrame(tick)
      else setDisplay(value)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [inView, value])

  const formatted =
    decimals > 0
      ? display.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
      : Math.round(display).toLocaleString('en-US')

  return (
    <span ref={ref}>
      {formatted}{suffix}
    </span>
  )
}

/** Aesthetic AI stat card with conic gradient ring + glow + unique icon */
function StatCard({ stat, index }) {
  const { key, label, value, suffix, decimals, change, gradient, icon } = stat
  const colors = gradientMap[gradient]

  return (
    <motion.div
      variants={itemVariants}
      className="stat-card relative group"
      whileHover={{ y: -6, transition: { duration: 0.25 } }}
    >
      {/* Floating glow background */}
      <div
        className="stat-glow"
        style={{ background: `radial-gradient(circle at 30% 20%, ${colors.glow}, transparent 70%)` }}
      />

      {/* Unique icon in gradient chip */}
      <div className="relative z-10 mb-4">
        <div
          className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center text-white shadow-lg transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3"
          style={{ background: `linear-gradient(135deg, ${colors.from}, ${colors.to})`, boxShadow: `0 8px 24px ${colors.glow}` }}
        >
          {icon}
        </div>
      </div>

      {/* Number */}
      <div className="relative z-10">
        <p className="stat-number" style={{ color: colors.from }}>
          <AnimatedNumber value={value} decimals={decimals} suffix={suffix} />
        </p>

        {/* Label */}
        <p className="stat-label">{label}</p>

        {/* Divider */}
        <div className="my-3 h-px w-12 mx-auto" style={{ background: `linear-gradient(90deg, transparent, ${colors.from}, transparent)` }} />

        {/* Trend row */}
        <div className="flex items-center justify-center gap-1.5">
          <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.8" className={`w-3 h-3 ${change.startsWith('-') ? 'text-rose-400 rotate-180' : 'text-emerald-400'}`}>
            <path d="M1 9L11 9M6 3v6M6 3L3 6M6 3l3 3" />
          </svg>
          <span className={`stat-change ${change.startsWith('-') ? 'text-rose-400' : 'text-emerald-400'}`}>{change}</span>
          <span className="text-slate-600 text-[10px]">this month</span>
        </div>
      </div>
    </motion.div>
  )
}

const features = [
  {
    icon: '⚡',
    title: 'Instant Prediction',
    desc: 'Get real-time academic performance predictions with our trained ML model. Results in milliseconds.',
    gradient: 'from-cyan-500 to-blue-500',
  },
  {
    icon: '🛡️',
    title: 'Transparent AI',
    desc: 'Every prediction comes with SHAP-based explanations. Understand exactly which factors influenced the result.',
    gradient: 'from-emerald-500 to-teal-500',
  },
  {
    icon: '💡',
    title: 'Actionable Insights',
    desc: 'Receive personalized recommendations to improve academic performance. Know exactly what areas need attention.',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    icon: '📊',
    title: 'Advanced Analytics',
    desc: 'Explore comprehensive analytics with interactive charts. Track performance trends and patterns.',
    gradient: 'from-amber-500 to-orange-500',
  },
]

const steps = [
  { icon: '📝', title: 'Input Student Data', desc: 'Enter academic records, study habits, and personal factors through our intuitive form.' },
  { icon: '⚡', title: 'Predict & Explain', desc: 'Our ML model analyzes 14+ features to generate predictions. SHAP explains every factor.' },
  { icon: '🎯', title: 'Get Recommendations', desc: 'Receive personalized, actionable recommendations to improve based on weak areas.' },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } }
}

export default function Home({ onNavigate }) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-24"
    >
      {/* Hero Section */}
      <section className="text-center py-16 md:py-24">
        <motion.div variants={itemVariants} className="max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm text-slate-300 mb-8">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            AI-Powered Academic Performance Prediction
          </div>
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-slate-100 leading-tight mb-6">
            Predict Student
            <br />
            <span className="gradient-text">Academic Performance</span>
          </h1>
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Analyze student academic data, estimate predicted percentage,
            explain every prediction using <strong className="text-slate-200">Explainable AI (SHAP)</strong>,
            and provide personalized recommendations for improvement.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <motion.button
              onClick={() => onNavigate('predict')}
              className="btn-primary text-lg px-8 py-4"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              🎯 Start Prediction
            </motion.button>
            <motion.button
              onClick={() => onNavigate('analytics')}
              className="btn-secondary text-lg px-8 py-4"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              📊 View Analytics
            </motion.button>
          </div>
        </motion.div>

        {/* AI Stats Grid */}
        <motion.div variants={itemVariants} className="ai-stats-grid mt-20 max-w-4xl mx-auto">
          {stats.map((stat, i) => (
            <StatCard key={stat.key} stat={stat} index={i} />
          ))}
        </motion.div>
      </section>

      {/* Features Section */}
      <section>
        <motion.div variants={itemVariants} className="text-center mb-12">
          <h2 className="section-title">
            Powerful Features for <span className="gradient-text">Accurate Predictions</span>
          </h2>
          <p className="section-subtitle mx-auto">
            Our platform combines cutting-edge ML with transparent SHAP explanations to deliver actionable insights.
          </p>
        </motion.div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={i}
              variants={itemVariants}
              className="glass-card text-center group cursor-default"
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
            >
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mx-auto mb-5 text-2xl shadow-lg transition-transform group-hover:scale-110`}>
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-slate-100 mb-3">{feature.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Performance Distribution Preview */}
      <section>
        <motion.div variants={itemVariants} className="glass-card">
          <h3 className="text-xl font-bold text-slate-100 mb-6">📊 Performance Distribution Overview</h3>
          <div className="space-y-4">
            {performanceDistribution.map((item) => (
              <div key={item.category} className="flex items-center gap-4">
                <span className="text-sm font-medium text-slate-300 w-24">{item.category}</span>
                <div className="flex-1 h-5 rounded-full bg-navy-800/60 overflow-hidden">
                  <motion.div
                    className="h-full rounded-full transition-all"
                    style={{ background: item.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${(item.count / 800) * 100}%` }}
                    transition={{ duration: 1, delay: 0.3, ease: 'easeOut' }}
                  />
                </div>
                <span className="text-sm text-slate-400 w-16 text-right">{item.count}</span>
                <span className="text-xs text-slate-500 w-14 text-right">{((item.count / 800) * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* How It Works */}
      <section>
        <motion.div variants={itemVariants} className="text-center mb-12">
          <h2 className="section-title">
            How It <span className="gradient-text">Works</span>
          </h2>
          <p className="section-subtitle mx-auto">
            Three simple steps to get transparent, explainable predictions.
          </p>
        </motion.div>
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, i) => (
            <motion.div
              key={i}
              variants={itemVariants}
              className="glass-card text-center relative"
            >
              {/* Step number */}
              <div className="absolute -top-4 -right-4 w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                {i + 1}
              </div>
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center mx-auto mb-5 text-3xl">
                {step.icon}
              </div>
              <h3 className="text-lg font-semibold text-slate-100 mb-3">{step.title}</h3>
              <p className="text-sm text-slate-400">{step.desc}</p>
            </motion.div>
          ))}
        </div>

        {/* Connecting arrows between steps (desktop) */}
        <div className="hidden md:flex justify-center mt-4 gap-40">
          {[0, 1].map((i) => (
            <div key={i} className="flex items-center">
              <div className="w-12 h-0.5 bg-gradient-to-r from-indigo-500/50 to-purple-500/50" />
              <div className="w-2 h-2 rotate-45 border-t-2 border-r-2 border-indigo-400/50 -ml-1" />
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <motion.section variants={itemVariants} className="glass-card text-center py-16 bg-gradient-to-r from-indigo-500/5 via-purple-500/5 to-cyan-500/5 border-indigo-500/20">
        <h2 className="text-3xl md:text-4xl font-extrabold text-slate-100 mb-4">
          Ready to Predict <span className="gradient-text">Student Performance?</span>
        </h2>
        <p className="text-slate-400 max-w-lg mx-auto mb-8">
          Start using the power of Explainable AI to make accurate, transparent predictions.
        </p>
        <motion.button
          onClick={() => onNavigate('predict')}
          className="btn-primary text-lg px-10 py-4"
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
        >
          🚀 Get Started Now
        </motion.button>
      </motion.section>
    </motion.div>
  )
}

