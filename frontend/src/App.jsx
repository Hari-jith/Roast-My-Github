import React, { useState } from 'react'
import LandingPage from './pages/LandingPage'
import LoadingPage from './pages/LoadingPage'
import ResultsDashboard from './pages/ResultsDashboard'
import ErrorPage from './pages/ErrorPage'
import { fetchRoast } from './api/github'

export default function App() {
  const [currentView, setCurrentView] = useState('landing')
  const [roastData, setRoastData] = useState(null)
  const [error, setError] = useState(null)
  const [analyzedUsername, setAnalyzedUsername] = useState('')

  const handleRoast = async (username) => {
    setAnalyzedUsername(username)
    setError(null)
    setCurrentView('loading')

    try {
      const data = await fetchRoast(username)
      setRoastData(data)
      setCurrentView('results')
    } catch (err) {
      setError(err?.message || (typeof err === 'string' ? err : 'Failed to analyze GitHub profile.'))
      setCurrentView('error')
    }
  }

  const handleReset = () => {
    setCurrentView('landing')
    setRoastData(null)
    setError(null)
    setAnalyzedUsername('')
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100">
      {currentView === 'landing' && (
        <LandingPage onRoast={handleRoast} />
      )}
      {currentView === 'loading' && (
        <LoadingPage username={analyzedUsername} />
      )}
      {currentView === 'results' && (
        <ResultsDashboard
          roastData={roastData}
          username={analyzedUsername}
          onReset={handleReset}
        />
      )}
      {currentView === 'error' && (
        <ErrorPage error={error} onReset={handleReset} />
      )}
    </div>
  )
}
