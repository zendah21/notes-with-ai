export type Priority = 'low' | 'medium' | 'high' | 'urgent'
export type Status = 'pending' | 'in_progress' | 'done'

export interface Task {
  id: number
  title: string
  description?: string | null
  status: Status
  priority: Priority
  estimated_duration_minutes?: number | null
  deadline_utc?: string | null
  notify_offsets_minutes?: number[] | null
  tags?: string[] | null
}

