import React from 'react'

export const Toolbar: React.FC<{
  filters: { status?: string; priority?: string; sort?: string; q?: string }
  onChange: (f: Partial<{status:string; priority:string; sort:string; q:string}>) => void
  onQuickAdd: (title: string) => void
  onAI: (utter: string) => void
}> = ({filters, onChange, onQuickAdd, onAI}) => {
  const [title, setTitle] = React.useState('')
  const [utter, setUtter] = React.useState("")
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
      <div className="lg:col-span-1">
        <div className="font-medium text-slate-700 mb-2">Filters</div>
        <div className="grid grid-cols-1 gap-2">
          <select className="form-select" value={filters.status||''} onChange={e=>onChange({status: e.target.value})}>
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In progress</option>
            <option value="done">Done</option>
          </select>
          <select className="form-select" value={filters.priority||''} onChange={e=>onChange({priority: e.target.value})}>
            <option value="">All priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
          <select className="form-select" value={filters.sort||'deadline'} onChange={e=>onChange({sort: e.target.value})}>
            <option value="deadline">Sort by deadline</option>
            <option value="created_desc">Newest first</option>
            <option value="title">Title A→Z</option>
          </select>
          <input className="form-input" placeholder="Search" value={filters.q||''} onChange={e=>onChange({q: e.target.value})} />
        </div>
      </div>
      <div className="lg:col-span-2">
        <div className="font-medium text-slate-700 mb-2">Quick add & AI</div>
        <div className="flex flex-col gap-2">
          <div className="flex gap-2">
            <input className="form-input flex-1" placeholder="Quick add task" value={title} onChange={e=>setTitle(e.target.value)} />
            <button className="btn btn-primary" onClick={()=>{ if (title.trim()) { onQuickAdd(title.trim()); setTitle('') } }}>Add</button>
          </div>
          <div className="flex gap-2">
            <input className="form-input flex-1" placeholder="Try: Move 'Rise email' to Fri 9:30, 20m, high, alert 1h" value={utter} onChange={e=>setUtter(e.target.value)} />
            <button className="btn btn-success" onClick={()=> onAI(utter)}>AI</button>
          </div>
        </div>
      </div>
    </div>
  )
}

