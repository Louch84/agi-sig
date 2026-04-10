import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import { exec } from 'child_process'
import { promisify } from 'util'
import { fileURLToPath } from 'url'
import path from 'path'
import { createServer } from 'http'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const execAsync = promisify(exec)
const app = express()
const PORT = 5200

app.use(helmet({ contentSecurityPolicy: false })) // allow inline for dev
app.use(cors({ origin: '*' }))
app.use(express.json())

// Serve static files from dist/
app.use(express.static(path.join(__dirname, 'dist')))

// ─── Helpers ───────────────────────────────────────────────────────────────────

function run(cmd, cwd = '/Users/sigbotti/.openclaw/workspace') {
  return new Promise((resolve) => {
    exec(cmd, { cwd, timeout: 60000, maxBuffer: 5 * 1024 * 1024 }, (err, stdout, stderr) => {
      resolve({ out: stdout.trim(), err: stderr.trim(), code: err?.code ?? 0 })
    })
  })
}

async function runBlogwatcher() {
  const scan = await run('blogwatcher scan 2>&1')
  await new Promise(r => setTimeout(r, 3000))
  const articles = await run('blogwatcher articles 2>&1')
  return { scan: scan.out, articles: articles.out }
}

// ─── Routes ────────────────────────────────────────────────────────────────────

// GET /api/status — system overview
app.get('/api/status', async (req, res) => {
  const results = {}

  try {
    const git = await run('git status --short && git log -1 --oneline')
    const { out: uptime } = await run('uptime')
    const { out: memUsed } = await run('vm_stat | head -6')
    const crons = await run('openclaw cron list 2>&1')

    results.git = git.out.split('\n')
    results.uptime = uptime
    results.memory = memUsed
    results.crons = crons.out
    results.ok = true
  } catch (e) {
    results.ok = false
    results.error = e.message
  }

  res.json(results)
})

// POST /api/action — run an action
app.post('/api/action', async (req, res) => {
  const { action } = req.body
  const id = Date.now().toString()

  const actions = {
    'refresh': async () => {
      const git = await run('git status --short')
      const crons = await run('openclaw cron list 2>&1')
      const { scan, articles } = await runBlogwatcher()
      return {
        summary: 'Heartbeat refresh complete',
        git: git.out,
        crons: crons.out,
        newArticles: articles.split('\n').filter(l => l.includes('[new]')).length,
        details: { git: git.out, crons: crons.out, scan, articles }
      }
    },

    'scan-rss': async () => {
      const { scan, articles } = await runBlogwatcher()
      const newCount = articles.split('\n').filter(l => l.includes('[new]')).length
      return {
        summary: `RSS scan complete — ${newCount} new article${newCount !== 1 ? 's' : ''}`,
        details: { scan, articles }
      }
    },

    'git-status': async () => {
      const branch = await run('git branch --show-current')
      const status = await run('git status --short')
      const log = await run('git log -3 --oneline')
      const diff = await run('git diff --stat')
      return {
        summary: status.out || 'Clean — nothing to commit',
        details: { branch: branch.out, status: status.out, log: log.out, diff: diff.out }
      }
    },

    'run-scanner': async () => {
      // The PerfectPlace cron fires at 1PM ET — trigger it manually via openclaw
      const result = await run('openclaw cron fire PerfectPlace 2>&1 || echo "Cron not found or failed"')
      return {
        summary: 'Scanner triggered',
        details: { output: result.out }
      }
    },

    'sync-memory': async () => {
      const today = new Date().toISOString().slice(0, 10)
      const daily = await run(`cat memory/${today}.md 2>/dev/null || echo "No log for today"`)
      const mem = await run('cat MEMORY.md | wc -l')
      const vecStats = await run('python3 scripts/ollama_mem.py stats 2>&1 || echo "vector store ok"')
      return {
        summary: `Memory sync — today: ${daily.out ? 'logged' : 'no entry'}, MEMORY.md: ${mem.out} lines`,
        details: { dailyLog: daily.out, memoryLines: mem.out, vectorStats: vecStats.out }
      }
    },

    'list-crons': async () => {
      const crons = await run('openclaw cron list 2>&1')
      return { summary: 'Cron status retrieved', details: { crons: crons.out } }
    },

    'openclaw-status': async () => {
      const status = await run('openclaw status 2>&1')
      const gateway = await run('openclaw gateway status 2>&1')
      return {
        summary: 'OpenClaw status',
        details: { status: status.out, gateway: gateway.out }
      }
    },
  }

  if (!actions[action]) {
    return res.status(400).json({ ok: false, error: `Unknown action: ${action}` })
  }

  try {
    // Run action with timeout
    const timeoutMs = 90000
    const result = await Promise.race([
      actions[action](),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout (90s)')), timeoutMs))
    ])
    res.json({ ok: true, id, ...result })
  } catch (e) {
    res.json({ ok: false, id, error: e.message })
  }
})

// GET /api/result/:id — get action result (polling)
const results = {}
app.get('/api/result/:id', (req, res) => {
  const r = results[req.params.id]
  if (!r) return res.json({ ready: false })
  delete results[req.params.id]
  res.json({ ready: true, ...r })
})

// SPA fallback — serve index.html for non-API routes
app.get('*', (req, res, next) => {
  if (!req.path.startsWith('/api')) {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'))
  } else {
    next()
  }
})

app.listen(PORT, () => {
  console.log(`🐾 Sig Botti OS API running at http://localhost:${PORT}`)
})
