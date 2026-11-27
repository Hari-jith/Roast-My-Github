import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { Code2, PieChart as PieIcon } from 'lucide-react'

const COLORS = [
  '#8b5cf6', // purple
  '#f97316', // orange
  '#3b82f6', // blue
  '#10b981', // green
  '#ec4899', // pink
  '#14b8a6', // teal
  '#ef4444', // red
  '#eab308', // yellow
  '#06b6d4', // cyan
  '#6366f1', // indigo
]

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div className="bg-[#12121a]/95 backdrop-blur-md border border-purple-500/30 p-2.5 rounded-xl shadow-2xl text-xs font-mono">
        <p className="font-bold text-white mb-0.5">{data.language}</p>
        <p className="text-purple-300">
          {data.percentage}% ({data.count} repo{data.count !== 1 ? 's' : ''})
        </p>
      </div>
    )
  }
  return null
}

export default function LanguageChart({ languageStats = [] }) {
  if (!languageStats || languageStats.length === 0) {
    return (
      <div className="bg-[#12121a] border border-purple-900/30 rounded-2xl p-6 shadow-lg shadow-purple-900/20 text-center">
        <div className="flex items-center gap-2 mb-4">
          <Code2 className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-bold text-white">Language Distribution</h3>
        </div>
        <div className="py-12 text-slate-500 flex flex-col items-center justify-center">
          <PieIcon className="w-10 h-10 text-slate-600 mb-2" />
          <p className="text-sm font-medium">No language data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-[#12121a] border border-purple-900/30 rounded-2xl p-6 shadow-lg shadow-purple-900/20">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Code2 className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-bold text-white">Language Distribution</h3>
        </div>
        <span className="text-xs font-mono text-slate-400">
          {languageStats.length} Language{languageStats.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Pie Chart */}
      <div className="w-full h-56 sm:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomTooltip />} />
            <Pie
              data={languageStats}
              dataKey="percentage"
              nameKey="language"
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={4}
              stroke="rgba(18, 18, 26, 0.8)"
              strokeWidth={3}
            >
              {languageStats.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                  className="hover:opacity-80 transition-opacity cursor-pointer"
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Custom Legend */}
      <div className="mt-4 pt-4 border-t border-purple-900/20 flex flex-wrap gap-2.5 justify-center">
        {languageStats.map((item, index) => (
          <div
            key={item.language}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.02] border border-white/5 text-xs font-mono"
          >
            <span
              className="w-2.5 h-2.5 rounded-full shrink-0"
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            />
            <span className="text-slate-300 font-medium">{item.language}</span>
            <span className="text-slate-500 font-semibold">{item.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
