import React from 'react'
import { motion } from 'framer-motion'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
}

const techStack = [
  { category: 'Frontend', items: 'React, Tailwind CSS, Framer Motion, Recharts' },
  { category: 'Backend', items: 'Python, Streamlit (ML Backend)' },
  { category: 'ML Models', items: 'Scikit-learn, XGBoost' },
  { category: 'XAI', items: 'SHAP (SHapley Additive exPlanations)' },
  { category: 'Data Processing', items: 'Pandas, NumPy' },
  { category: 'Visualization', items: 'Recharts, Plotly' },
]

const models = [
  { name: 'Logistic Regression', desc: 'Baseline linear model', accuracy: '84.2%' },
  { name: 'Decision Tree', desc: 'Interpretable tree-based model', accuracy: '87.1%' },
  { name: 'Random Forest', desc: 'Ensemble of decision trees (Best)', accuracy: '94.2%' },
  { name: 'XGBoost', desc: 'Gradient boosting', accuracy: '93.8%' },
]

export default function About() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="glass rounded-2xl p-8 text-center bg-gradient-to-r from-indigo-500/5 via-purple-500/5 to-cyan-500/5">
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-100 mb-4">
          📚 About <span className="gradient-text">EduPredict AI</span>
        </h1>
        <p className="text-slate-400 max-w-2xl mx-auto">
          Explainable AI Based Student Academic Performance Prediction System
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-xl font-bold text-slate-100 mb-4">🎯 Project Overview</h3>
            <p className="text-sm text-slate-400 leading-relaxed mb-4">
              This <strong className="text-slate-200">B.Tech Final Year Project</strong> combines
              <strong className="text-slate-200"> Machine Learning</strong> with
              <strong className="text-slate-200"> Explainable AI (XAI)</strong> to create a transparent
              and interpretable student performance prediction system.
            </p>
            <p className="text-sm text-slate-400 leading-relaxed">
              The system analyzes 14+ student features including academic records, behavioral patterns,
              and engagement factors to predict performance with 94.2% accuracy. Every prediction
              is accompanied by SHAP-based explanations showing exactly which factors influenced the result.
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-xl font-bold text-slate-100 mb-4">✨ Key Features</h3>
            <div className="grid sm:grid-cols-2 gap-4">
              {[
                { icon: '🎯', title: 'Performance Prediction', desc: 'Predict student performance using ML models with 94.2% accuracy' },
                { icon: '🔍', title: 'Explainable AI', desc: 'SHAP-based explanations for every prediction, showing feature contributions' },
                { icon: '📊', title: 'Interactive Analytics', desc: 'Explore performance factors through interactive charts and visualizations' },
                { icon: '🤖', title: 'Model Comparison', desc: 'Multiple ML models with automatic best model selection' },
                { icon: '💡', title: 'Recommendation Engine', desc: 'Personalized improvement suggestions based on weak areas' },
                { icon: '📋', title: 'History Tracking', desc: 'Track and export prediction history for analysis' },
              ].map((feature, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-navy-800/30">
                  <span className="text-xl">{feature.icon}</span>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-200">{feature.title}</h4>
                    <p className="text-xs text-slate-400 mt-1">{feature.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-xl font-bold text-slate-100 mb-4">📊 Dataset</h3>
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-navy-800/30">
                <p className="text-3xl font-bold text-indigo-400">1,200</p>
                <p className="text-sm text-slate-400">Student Records</p>
              </div>
              <div className="p-4 rounded-xl bg-navy-800/30">
                <p className="text-3xl font-bold text-emerald-400">14+</p>
                <p className="text-sm text-slate-400">Features Analyzed</p>
              </div>
              <div className="p-4 rounded-xl bg-navy-800/30">
                <p className="text-3xl font-bold text-cyan-400">4</p>
                <p className="text-sm text-slate-400">Performance Categories</p>
              </div>
              <div className="p-4 rounded-xl bg-navy-800/30">
                <p className="text-3xl font-bold text-amber-400">94.2%</p>
                <p className="text-sm text-slate-400">Model Accuracy</p>
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4">
              Features include academic, behavioral, and engagement factors. Target: Performance categories
              (Poor, Average, Good, Excellent). No personally identifiable information is stored.
            </p>
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-lg font-bold text-slate-100 mb-4">🛠️ Technology Stack</h3>
            <div className="space-y-3">
              {techStack.map((tech, i) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="w-2 h-2 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-slate-300">{tech.category}</p>
                    <p className="text-xs text-slate-500">{tech.items}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-lg font-bold text-slate-100 mb-4">🤖 Models Compared</h3>
            <div className="space-y-3">
              {models.map((model, i) => (
                <div key={i} className="p-3 rounded-xl bg-navy-800/30">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-semibold text-slate-200">{model.name}</p>
                    <span className="text-xs font-bold text-indigo-400">{model.accuracy}</span>
                  </div>
                  <p className="text-xs text-slate-500">{model.desc}</p>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-lg font-bold text-slate-100 mb-4">📁 Project Structure</h3>
            <div className="bg-navy-950/50 rounded-xl p-4 font-mono text-xs">
              <p className="text-slate-400">Student_Performance_XAI/</p>
              <p className="text-slate-500 ml-4">├── dataset/</p>
              <p className="text-slate-500 ml-4">├── src/</p>
              <p className="text-slate-500 ml-4">├── models/</p>
              <p className="text-slate-500 ml-4">├── xai/</p>
              <p className="text-slate-500 ml-4">├── app/</p>
              <p className="text-slate-500 ml-4">└── reports/</p>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card">
            <h3 className="text-lg font-bold text-slate-100 mb-4">⚠️ Disclaimer</h3>
            <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/10">
              <p className="text-xs text-amber-400/80 leading-relaxed">
                This is a <strong className="text-amber-300">decision-support tool only</strong>.
                It does not measure actual student intelligence or guarantee future success.
                The SHAP explanations show model behavior, not real-world causation.
                The model is trained on synthetic data and should be validated with real-world
                data before deployment.
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
