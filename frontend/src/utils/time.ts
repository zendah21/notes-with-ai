export function formatUtc(iso?: string | null) {
  if (!iso) return ''
  try { return new Date(iso).toISOString().replace('.000','').replace('T',' ').replace('Z',' UTC') } catch { return String(iso) }
}
export function formatLocal(iso?: string | null) {
  if (!iso) return ''
  try { return new Date(iso).toLocaleString() } catch { return String(iso) }
}

