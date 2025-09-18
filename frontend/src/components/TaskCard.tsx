import React, { useState } from 'react'
import type { Task } from '@/types'
import { CardHeader } from './CardHeader'
import { CardMeta } from './CardMeta'
import { CardActions } from './CardActions'
import { ScheduleEditor } from './ScheduleEditor'

export const TaskCard: React.FC<{task: Task; onChange?: (t: Partial<Task>)=>void; onDelete?: ()=>void}> = ({task, onChange, onDelete}) => {
  const [schedOpen, setSchedOpen] = useState(false)
  const titleId = `task-${task.id}-title`
  return (
    <article className="h-full flex flex-col rounded-card shadow-card bg-white border border-slate-200/60" aria-labelledby={titleId}>
      <CardHeader title={task.title} status={task.status} titleId={titleId} />
      <CardMeta priority={task.priority} duration={task.estimated_duration_minutes ?? undefined} deadlineUtc={task.deadline_utc ?? undefined} alerts={task.notify_offsets_minutes ?? undefined} />
      {task.description && (
        <section className="px-4 pb-2">
          <p className="text-sm text-slate-600 line-clamp-3">{task.description}</p>
        </section>
      )}
      <CardActions
        onScheduleOpen={()=> setSchedOpen(true)}
        onComplete={()=> onChange?.({status:'done'})}
        onReopen={()=> onChange?.({status:'pending'})}
        onDelete={()=> onDelete?.()}
      />
      <ScheduleEditor open={schedOpen} onClose={()=>setSchedOpen(false)} onSave={(v)=>{
        onChange?.({
          estimated_duration_minutes: v.duration,
          // Backend should parse when/alerts; here we keep UI contract only
        })
      }} />
    </article>
  )
}

