import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Home from './components/Home'
import Predict from './components/Predict'
import Analytics from './components/Analytics'
import XAI from './components/XAI'
import History from './components/History'
import About from './components/About'
import { motion, AnimatePresence } from 'framer-motion'

const PAGES = {
  HOME: 'home',
  PREDICT: 'predict',
  ANALYTICS: 'analytics',
  XAI: 'xai',
  HISTORY: 'history',
  ABOUT: 'about'
}

export default function App() {
  const [currentPage, setCurrentPage] = useState(PAGES.HOME)
  const [predictionHistory, setPredictionHistory] = useState([])
  const [lastPrediction, setLastPrediction] = useState(null)
  const [lastStudentData, setLastStudentData] = useState(null)

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('edupredict_history')
      if (saved) {
        setPredictionHistory(JSON.parse(saved))
      }
    } catch (e) {
      console.warn('Failed to load history:', e)
    }
  }, [])

  // Save history to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('edupredict_history', JSON.stringify(predictionHistory))
  }, [predictionHistory])

  const addToHistory = (studentData, result) => {
    const record = {
      id: Date.now(),
      date: new Date().toLocaleString(),
      studentName: studentData.studentName || 'Unnamed Student',
      ...studentData,
      ...result
    }
    setPredictionHistory(prev => [record, ...prev])
    setLastPrediction(result)
    setLastStudentData(studentData)
  }

  const clearHistory = () => {
    setPredictionHistory([])
  }

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
    exit: { opacity: 0, y: -20, transition: { duration: 0.2 } }
  }

  const renderPage = () => {
    const PageComponent = {
      [PAGES.HOME]: Home,
      [PAGES.PREDICT]: Predict,
      [PAGES.ANALYTICS]: Analytics,
      [PAGES.XAI]: XAI,
      [PAGES.HISTORY]: History,
      [PAGES.ABOUT]: About
    }[currentPage]

    return (
      <motion.div
        key={currentPage}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className="min-h-[calc(100vh-4rem)]"
      >
        <PageComponent
          onNavigate={setCurrentPage}
          addToHistory={addToHistory}
          lastPrediction={lastPrediction}
          lastStudentData={lastStudentData}
          predictionHistory={predictionHistory}
          clearHistory={clearHistory}
          setCurrentPage={setCurrentPage}
        />
      </motion.div>
    )
  }

  return (
    <div className="min-h-screen bg-navy-950">
      {/* Background gradient orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/3 -right-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl" />
      </div>

      {/* Navbar */}
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} pages={PAGES} />

      {/* Page Content */}
      <main className="relative z-10 pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <AnimatePresence mode="wait">
          {renderPage()}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-indigo-500/10 bg-navy-900/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                E
              </div>
              <span className="text-slate-400 font-semibold">EduPredict AI</span>
            </div>
            <p className="text-sm text-slate-500">
              © 2024-2025 EduPredict AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

