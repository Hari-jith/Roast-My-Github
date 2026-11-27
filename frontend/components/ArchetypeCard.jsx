import React from 'react'
import { Sparkles, HelpCircle } from 'lucide-react'

const ARCHETYPE_ICONS = {
  'tutorial collector': '📚',
  'museum curator': '🏛️',
  'framework hopper': '🔀',
  'repository hoarder': '📦',
  'one-project perfectionist': '🎯',
  'documentation optimist': '📝',
  'quietly competent': '⚡',
  'ghost committer': '👻',
  'aspiring developer': '🌱',
}

export default function ArchetypeCard({ archetype }) {
  if (!archetype) return null

  const title = archetype.title || 'The Code Enigma'
  const cleanTitle = title.toLowerCase().replace(/the\s+/, '').trim()
  const emoji = ARCHETYPE_ICONS[cleanTitle] || '💻'

  const confidence = (archetype.confidence || 'medium').toLowerCase()

  let confidenceBadgeStyle = 'bg-yellow-500/10 text-yellow-300 border-yellow-500/30'
  if (confidence === 'high') {
    confidenceBadgeStyle = 'bg-purple-500/10 text-purple-300 border-purple-500/30 glow-purple'
  } else if (confidence === 'low') {
    confidenceBadgeStyle = 'bg-slate-500/10 text-slate-400 border-slate-500/30'
  }

  return (
    <div className="bg-[#12121a] border border-purple-900/30 rounded-2xl p-6 sm:p-7 shadow-lg shadow-purple-900/20 relative overflow-hidden transition-all duration-300 hover:border-purple-800/40">
      {/* Background glow banner */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-purple-600/10 via-pink-600/5 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Header with confidence badge */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <span className="text-xs font-mono uppercase tracking-widest text-slate-400 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-orange-400" /> Developer Archetype
        </span>
        <span className={`text-[11px] font-mono uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${confidenceBadgeStyle}`}>
          {confidence} Confidence
        </span>
      </div>

      {/* Archetype Icon & Title */}
      <div className="flex items-start sm:items-center gap-4 mb-4">
        <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gradient-to-br from-purple-950/80 to-slate-900/90 border border-purple-700/30 flex items-center justify-center text-3xl sm:text-4xl shadow-md shrink-0">
          {emoji}
        </div>
        <div>
          <h3 className="text-2xl sm:text-3xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent leading-tight">
            {title}
          </h3>
          <p className="text-slate-300 text-sm sm:text-base font-medium mt-1">
            {archetype.description}
          </p>
        </div>
      </div>

      {/* Explanation Box */}
      {archetype.explanation && (
        <div className="mt-4 p-4 rounded-xl bg-white/[0.02] border border-white/5">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 mb-1">
            <HelpCircle className="w-3.5 h-3.5 text-purple-400" />
            <span>Why this archetype?</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            {archetype.explanation}
          </p>
        </div>
      )}
    </div>
  )
}
