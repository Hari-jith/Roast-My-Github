import React, { useState, useEffect } from 'react'
import { ChevronDown, ChevronUp, AlertCircle, Flame, ShieldAlert } from 'lucide-react'

export default function ChaosScoreCard({ chaosScore }) {
  const [displayScore, setDisplayScore] = useState(0)
  const [showBreakdown, setShowBreakdown] = useState(false)

  const total = chaosScore?.total ?? 0
  const breakdown = chaosScore?.breakdown || []
  const interpretation = chaosScore?.interpretation || 'Analysis completed.'
  const disclaimer = chaosScore?.disclaimer || 'Scores are calculated algorithmically based on public repo patterns.'

  // Animate counter from 0 to total
  useEffect(() => {
    let current = 0
    const step = Math.max(1, Math.ceil(total / 30))
    const timer = setInterval(() => {
      current += step
      if (current >= total) {
        setDisplayScore(total)
        clearInterval(timer)
      } else {
        setDisplayScore(current)
      }
    }, 25)

    return () => clearInterval(timer)
  }, [total])

  // Determine styling based on score ranges
  let strokeColor = '#22c55e'
  let textColorClass = 'text-emerald-400'
  let glowClass = ''
  let severityLabel = 'Minimal Chaos'

  if (total <= 20) {
    strokeColor = '#22c55e'
    textColorClass = 'text-emerald-400'
    severityLabel = 'Minimal Chaos'
  } else if (total <= 40) {
    strokeColor = '#eab308'
    textColorClass = 'text-yellow-400'
    severityLabel = 'Mild Disarray'
  } else if (total <= 60) {
    strokeColor = '#f97316'
    textColorClass = 'text-orange-500'
    severityLabel = 'Significant Chaos'
  } else if (total <= 80) {
    strokeColor = '#ef4444'
    textColorClass = 'text-red-500'
    severityLabel = 'High Disorder'
  } else {
    strokeColor = '#dc2626'
    textColorClass = 'text-rose-500'
    glowClass = 'drop-shadow-[0_0_15px_rgba(239,68,68,0.7)]'
    severityLabel = 'Absolute Cataclysm 🔥'
  }

  // SVG circle calculation
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (displayScore / 100) * circumference

  return (
    <div className="bg-[#12121a] border border-purple-900/30 rounded-2xl p-6 shadow-lg shadow-purple-900/20 relative overflow-hidden transition-all duration-300 hover:border-purple-800/40">
      {/* Background radial accent */}
      <div className="absolute top-0 left-0 w-48 h-48 bg-orange-600/5 rounded-full blur-2xl pointer-events-none" />

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-orange-400" />
          <h3 className="text-lg font-bold text-white tracking-wide">Chaos Score</h3>
        </div>
        <span className={`text-xs font-mono font-semibold px-2.5 py-1 rounded-full border border-white/10 ${textColorClass} bg-white/[0.03]`}>
          {severityLabel}
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-6 my-4">
        {/* Animated Circular Gauge */}
        <div className="relative w-36 h-36 flex items-center justify-center shrink-0">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 128 128">
            {/* Background ring */}
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="10"
              fill="transparent"
            />
            {/* Animated progress ring */}
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke={strokeColor}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className={`transition-all duration-500 ease-out ${glowClass}`}
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center text-center">
            <span className={`text-3xl sm:text-4xl font-black font-mono leading-none ${textColorClass}`}>
              {displayScore}
            </span>
            <span className="text-[11px] font-mono text-slate-400 mt-0.5">/ 100</span>
          </div>
        </div>

        {/* Interpretation */}
        <div className="flex-1 text-center sm:text-left">
          <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-1 font-mono">
            Diagnostic Summary
          </h4>
          <p className="text-slate-200 text-sm sm:text-base leading-relaxed">
            {interpretation}
          </p>
        </div>
      </div>

      {/* Accordion Toggle */}
      {breakdown.length > 0 && (
        <div className="mt-4 pt-4 border-t border-purple-900/20">
          <button
            type="button"
            onClick={() => setShowBreakdown(!showBreakdown)}
            className="w-full flex items-center justify-between text-xs font-semibold text-purple-300 hover:text-purple-200 py-1 transition-colors"
          >
            <span>Score Breakdown ({breakdown.length} Factors)</span>
            {showBreakdown ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          {/* Breakdown Items */}
          {showBreakdown && (
            <div className="mt-3 space-y-3 animate-slide-up">
              {breakdown.map((item, idx) => {
                const percent = Math.min(100, Math.round((item.score / (item.max_score || 25)) * 100))
                return (
                  <div key={idx} className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                    <div className="flex justify-between items-center text-xs mb-1.5">
                      <span className="font-semibold text-slate-200">{item.factor}</span>
                      <span className="font-mono text-slate-400">
                        {item.score} / {item.max_score} pts
                      </span>
                    </div>
                    {/* Progress Bar */}
                    <div className="w-full bg-[#1b1b28] rounded-full h-1.5 overflow-hidden mb-1.5">
                      <div
                        className="h-full bg-gradient-to-r from-purple-500 to-orange-500 rounded-full"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    {item.explanation && (
                      <p className="text-[11px] text-slate-400 leading-tight">
                        {item.explanation}
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Disclaimer */}
      <p className="mt-4 text-[11px] text-slate-500 italic text-center sm:text-left flex items-center gap-1.5">
        <AlertCircle className="w-3 h-3 shrink-0 text-slate-600" />
        <span>{disclaimer}</span>
      </p>
    </div>
  )
}
