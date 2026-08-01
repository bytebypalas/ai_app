 import React from 'react'
import { motion } from 'framer-motion'
import { performanceDistribution } from '../data/sampleData'
import { formatNumber } from '../utils/helpers'

const stats = [
  { label: 'Students Analyzed', value: '1,200+', change: '+12%', gradient: 'from-indigo-500 to-purple-600' },
  { label: 'Model Accuracy', value: '94.2%', change: '+5.2%', gradient: 'from-emerald-500 to-teal-500' },
  { label: 'Features Analyzed', value: '14+', change: '+3', gradient: 'from-cyan-500 to-blue-600' },
  { label: 'Predictions Made', value: '5,800+', change: '+18%', gradient: 'from-amber-500 to-orange-500' },
]

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

        {/* Stats Grid */}
        <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-20 max-w-4xl mx-auto">
          {stats.map((stat, i) => (
            <div key={i} className="glass rounded-2xl p-5 text-center">
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${stat.gradient} flex items-center justify-center mx-auto mb-3`}>
                <span className="text-white text-sm font-bold">●</span>
              </div>
              <p className="text-2xl md:text-3xl font-bold text-slate-100">{stat.value}</p>
              <p className="text-xs text-slate-400 mt-1">{stat.label}</p>
              <p className="text-xs text-emerald-400 mt-0.5">{stat.change}</p>
            </div>
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

