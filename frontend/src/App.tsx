import React, { useEffect, useMemo, useState } from 'react'
import { Toolbar } from './components/Toolbar'
import { StatsBar } from './components/StatsBar'
import { TaskCard } from './components/TaskCard'
import type { Task } from './types'

const DEMO: Task[] = [
  { id: 1, title: 'Write polite rejection email', status: 'pending', priority: 'high', estimated_duration_minutes: 30, deadline_utc: '2025-09-16T22:30:00Z', notify_offsets_minutes: [60, 720] },
  { id: 2, title: 'Rise email', status: 'done', priority: 'high', estimated_duration_minutes: 20, notify_offsets_minutes: [20] },
  { id: 3, title: 'New Task', status: 'pending', priority: 'medium' }
]

export default function App(){
  const [tasks, setTasks] = useState<Task[]>(DEMO)
  const [filters, setFilters] = useState<{status?:string; priority?:string; sort?:string; q?:string}>({ sort: 'deadline' })

  const filtered = useMemo(()=>{
    let arr = [...tasks]
    if (filters.status) arr = arr.filter(t=>t.status===filters.status)
    if (filters.priority) arr = arr.filter(t=>t.priority===filters.priority)
    if (filters.q) arr = arr.filter(t=> (t.title + ' ' + (t.description||'')).toLowerCase().includes(filters.q!.toLowerCase()))
    if (filters.sort==='title') arr.sort((a,b)=> a.title.localeCompare(b.title))
    if (filters.sort==='created_desc') arr = arr.reverse()
    // deadline sort basic
    if (filters.sort==='deadline') arr.sort((a,b)=> (a.deadline_utc?Date.parse(a.deadline_utc):Infinity) - (b.deadline_utc?Date.parse(b.deadline_utc):Infinity))
    return arr
  }, [tasks, filters])

  const stats = useMemo(()=>({
    total: tasks.length,
    pending: tasks.filter(t=>t.status==='pending').length,
    inProgress: tasks.filter(t=>t.status==='in_progress').length,
    done: tasks.filter(t=>t.status==='done').length,
  }), [tasks])

  function updateTask(id:number, patch: Partial<Task>){
    setTasks(prev => prev.map(t => t.id===id ? {...t, ...patch}: t))
  }
  function deleteTask(id:number){ setTasks(prev => prev.filter(t=>t.id!==id)) }

  // TODO: wire to Flask API; proxy in vite.config.ts already set
  // useEffect(()=>{ fetch('/api/tasks').then(r=>r.json()).then(setTasks) },[])

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-4">
      <header className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold">Tasks</h1>
          <p className="text-slate-500">Plan, prioritize and schedule your tasks with AI assistance.</p>
        </div>
        <div className="flex gap-2">
          <a className="btn btn-secondary" href="/help">Help</a>
          <a className="btn btn-success" href="/ai/console">AI Console</a>
        </div>
      </header>

      <div className="rounded-card border bg-white p-4 shadow-card">
        <Toolbar
          filters={filters}
          onChange={(f)=> setFilters(prev=> ({...prev, ...f}))}
          onQuickAdd={(title)=> setTasks(prev=> [...prev, { id: Date.now(), title, status:'pending', priority:'medium'}])}
          onAI={(utter)=> console.log('AI utter:', utter)}
        />
      </div>

      <StatsBar total={stats.total} pending={stats.pending} inProgress={stats.inProgress} done={stats.done} />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
        {filtered.length===0 && (
          <div className="col-span-full rounded-card border bg-white p-8 text-center text-slate-500 shadow-card">No tasks match your filters.</div>
        )}
        {filtered.map(t => (
          <TaskCard key={t.id} task={t} onChange={(p)=> updateTask(t.id, p)} onDelete={()=> deleteTask(t.id)} />
        ))}
      </div>
    </div>
  )
}

