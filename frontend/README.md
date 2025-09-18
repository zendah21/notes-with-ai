AI Notes Frontend (React + Tailwind)

Overview
- Vite + React + TypeScript + Tailwind
- Components: Board/Toolbar/StatsBar/TaskCard/Chip (+ subcomponents)
- Proxy to Flask API/WebSocket via vite.config.ts

Run locally
- cd frontend
- npm install
- npm run dev
- Open http://localhost:5173

Wire to Flask API
- Update data fetch in src/App.tsx (see TODO) to call your Flask endpoints.
- Proxy already set for /api and /ws to http://127.0.0.1:5000.

Folders
- src/components: Chip, TaskCard, CardHeader, CardMeta, CardActions, ScheduleEditor, Toolbar, StatsBar
- src/types.ts: shared task types
- src/icons.tsx: lightweight SVG icons

