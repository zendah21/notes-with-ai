import React from 'react'

export const CardActions: React.FC<{
  onComplete: () => void
  onReopen: () => void
  onDelete: () => void
  onScheduleOpen: () => void
  isSaving?: boolean
}> = ({onComplete, onReopen, onDelete, onScheduleOpen, isSaving}) => {
  return (
    <footer className="mt-auto px-4 pb-4 flex items-center justify-between">
      <button className="btn btn-secondary" onClick={onScheduleOpen}>Schedule</button>
      <div className="flex gap-2">
        <button className="btn btn-ghost" onClick={onComplete} aria-pressed={false} disabled={isSaving}>Complete</button>
        <button className="btn btn-ghost" onClick={onReopen} aria-pressed={false} disabled={isSaving}>Reopen</button>
        <button className="btn btn-ghost text-rose-600 border-rose-200" onClick={onDelete} disabled={isSaving}>Delete</button>
      </div>
    </footer>
  )
}

