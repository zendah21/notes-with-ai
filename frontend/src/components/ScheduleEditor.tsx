import React, { useState } from 'react'

export const ScheduleEditor: React.FC<{
  open: boolean
  onClose: () => void
  onSave: (v:{when?:string; duration?:number; alerts?:string}) => void
}> = ({open, onClose, onSave}) => {
  const [when, setWhen] = useState('')
  const [duration, setDuration] = useState<number|undefined>()
  const [alerts, setAlerts] = useState('')
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative bg-white rounded-card shadow-card w-[22rem] p-4 space-y-3">
        <h4 className="text-sm font-semibold">Schedule</h4>
        <div className="space-y-2">
          <label className="block text-sm">When
            <input className="mt-1 block w-full rounded-md border-slate-300" placeholder="Fri 9:30 or tomorrow 10am" value={when} onChange={e=>setWhen(e.target.value)} />
          </label>
          <label className="block text-sm">Duration (min)
            <input type="number" className="mt-1 block w-full rounded-md border-slate-300" value={duration ?? ''} onChange={e=>setDuration(e.target.value? Number(e.target.value):undefined)} />
          </label>
          <label className="block text-sm">Alerts
            <input className="mt-1 block w-full rounded-md border-slate-300" placeholder="1h, 30m" value={alerts} onChange={e=>setAlerts(e.target.value)} />
          </label>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={()=>{ onSave({when, duration, alerts}); onClose(); }}>Save</button>
        </div>
      </div>
    </div>
  )
}

