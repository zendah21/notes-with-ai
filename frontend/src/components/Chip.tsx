import React from 'react'

type Variant = 'neutral'|'time'|'low'|'medium'|'high'|'urgent'|'pending'|'done'
type Size = 'sm'|'md'

export const Chip: React.FC<{variant?: Variant; size?: Size; title?: string; className?: string; children: React.ReactNode}> = ({variant='neutral', size='sm', title, className, children}) => {
  const base = 'inline-flex items-center rounded-full font-medium leading-tight'
  const sizes: Record<Size, string> = { sm: 'text-xs px-2 py-0.5 gap-1', md: 'text-sm px-3 py-1 gap-1.5' }
  const variants: Record<Variant, string> = {
    neutral: 'bg-slate-100 text-slate-700',
    time: 'bg-slate-50 text-slate-600 border border-slate-200',
    low: 'bg-priority-low-bg text-priority-low-fg',
    medium: 'bg-priority-medium-bg text-priority-medium-fg',
    high: 'bg-priority-high-bg text-priority-high-fg',
    urgent: 'bg-priority-urgent-bg text-priority-urgent-fg',
    pending: 'bg-status-pending-bg text-status-pending-fg',
    done: 'bg-status-done-bg text-status-done-fg',
  }
  return <span title={title} className={[base, sizes[size], variants[variant], className].filter(Boolean).join(' ')}>{children}</span>
}

