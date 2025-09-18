import React from 'react'
import { Chip } from './Chip'

export const StatsBar: React.FC<{total:number; pending:number; inProgress:number; done:number}> = ({total, pending, inProgress, done}) => {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Chip variant="neutral">Total: {total}</Chip>
      <Chip variant="pending">Pending: {pending}</Chip>
      <Chip variant="time" className="bg-amber-50 text-amber-700">In progress: {inProgress}</Chip>
      <Chip variant="done">Done: {done}</Chip>
    </div>
  )
}

