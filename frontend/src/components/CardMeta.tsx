import React from 'react'
import { Chip } from './Chip'
import { Bell, Calendar, Clock } from '@/icons'
import type { Priority } from '@/types'
import { formatLocal, formatUtc } from '@/utils/time'

export const CardMeta: React.FC<{priority: Priority; duration?: number|null; deadlineUtc?: string|null; alerts?: number[]|null}> = ({priority, duration, deadlineUtc, alerts}) => {
  return (
    <section className="px-4 pb-2">
      <ul className="flex flex-wrap gap-2 items-center" aria-label="Task metadata">
        <li><Chip variant={priority} size="sm">{priority}</Chip></li>
        {typeof duration === 'number' && duration > 0 && (
          <li><Chip variant="time" size="sm"><Clock className="mr-1 h-3 w-3" aria-hidden /> {duration}m</Chip></li>
        )}
        {deadlineUtc && (
          <li>
            <Chip variant="time" size="sm" title={`Local: ${formatLocal(deadlineUtc)}`}>
              <Calendar className="mr-1 h-3 w-3" aria-hidden /> {formatUtc(deadlineUtc)}
            </Chip>
          </li>
        )}
        {alerts && alerts.length > 0 && (
          <li>
            <Chip variant="time" size="sm"><Bell className="mr-1 h-3 w-3" aria-hidden /> {alerts.map(m=> m<60? `${m}m`:`${Math.round(m/60)}h`).join(', ')}</Chip>
          </li>
        )}
      </ul>
    </section>
  )
}

