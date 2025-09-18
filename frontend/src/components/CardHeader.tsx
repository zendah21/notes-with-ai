import React from 'react'
import { Chip } from './Chip'
import type { Status } from '@/types'

export const CardHeader: React.FC<{title: string; status: Status; titleId: string}> = ({title, status, titleId}) => {
  return (
    <header className="px-4 pt-4 pb-2 flex items-start justify-between">
      <h3 id={titleId} className="text-base font-semibold text-slate-900">{title}</h3>
      <Chip variant={status === 'done' ? 'done' : 'pending'} size="sm">{status.replace('_',' ')}</Chip>
    </header>
  )
}

