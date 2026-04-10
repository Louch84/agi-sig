import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import { exec } from 'child_process'
import { fileURLToPath } from 'url'
import path from 'path'
import os from 'os'
import simpleGit from 'simple-git'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const WORKSPACE = '/Users/sigbotti/.openclaw/workspace'
const git = simpleGit(WORKSPACE)
const app = express()
const PORT = 5200

app.use(helmet({ contentSecurityPolicy: false }))
app.use(cors({ origin: '*' }))
app.use(express.json())
app.use(express.static(path.join(__dirname, 'dist')))

function run(cmd, cwd = WORKSPACE) {
  return new Promise((resolve) => {
    exec(cmd, { cwd, timeout: 10, killSignal: 'SIGKILL' }, (err, stdout, stderr) => {
      resolve({ out: (stdout || '').toString().trim(), err: (stderr || '').toString().trim(), code: err?.code ?? 0 })
    })
  })
}

// ─── Status ────────────────────────────────────────────────────────────────────
app.get('/api/status', async (req, res) => {
  let gitStatus = []
  let gitLog = ''
  try {
    const status = await git.status()
    gitStatus = status.current ? [`${status.current} ${status.tracking || ''}`] : []
    const log = await git.log({ maxCount: 1 })
    gitLog = log.latest ? `${log.latest.hash.slice(0, 8)} ${log.latest.message}` : ''
  } catch (e) {
    gitStatus = ['git error: ' + e.message]
  }

  const uptimeSecs = os.uptime()
  const days = Math.floor(uptimeSecs / 86400)
  const hours = Math.floor((uptimeSecs % 86400) / 3600)
  const mins = Math.floor((uptimeSecs % 3600) / 60)
  const uptime = days > 0 ? `${days}d ${hours}h ${mins}m` : `${hours}h ${mins}m`

  const openClaw = await run('ps aux | grep -c "[o]penclaw"')

  res.json({
    ok: true,
    git: [...gitStatus, gitLog].filter(Boolean),
    uptime: `up ${days}d ${hours}h ${mins}m`,
    openClawProcs: openClaw.out.trim() || '1',
  })
})

// ─── Actions ───────────────────────────────────────────────────────────────────
app.post('/api/action', async (req, res) => {
  const { action } = req.body
  const id = Date.now().toString()

  const actions = {
    'refresh': async () => {
      const status = await git.status()
      const log = await runBlogwatcherScan()
      const newCount = (log.match(/\[new\]/g) || []).length
      return { summary: `Refresh done — ${newCount} new article${newCount !== 1 ? 's' : ''}`, details: { status: status.current, tracking: status.tracking } }
    },
    'scan-rss': async () => {
      const result = await runBlogwatcherScan()
      const newCount = (result.match(/\[new\]/g) || []).length
      return { summary: `RSS scan done — ${newCount} new article${newCount !== 1 ? 's' : ''}` }
    },
    'git-status': async () => {
      const status = await git.status()
      const log = await git.log({ maxCount: 3 })
      const diff = await git.diffSummary()
      return {
        summary: status.current ? `${status.current} ${status.tracking || ''}` : 'No git status',
        details: {
          branch: status.current || '',
          status: status.modified?.length ? `${status.modified.length} modified` : 'clean',
          staged: status.staged?.length || 0,
          log: log.all?.slice(0, 3).map(l => `${l.hash.slice(0, 8)} ${l.message}`).join('\n') || '',
          diff: diff.summary || '',
        }
      }
    },
    'run-scanner': async () => {
      const r = await run('openclaw cron fire PerfectPlace 2>&1 || echo "not available"')
      return { summary: 'Scanner triggered', details: { output: r.out || r.err } }
    },
    'sync-memory': async () => {
      const today = new Date().toISOString().slice(0, 10)
      const [daily, memLines, vec] = await Promise.all([
        run(`cat ${WORKSPACE}/memory/${today}.md 2>/dev/null || echo "no entry"`),
        run(`wc -l < ${WORKSPACE}/MEMORY.md`),
        run('python3 scripts/ollama_mem.py stats 2>&1 || echo "ok"'),
      ])
      return { summary: `Memory — today: ${daily.out === 'no entry' ? 'no log' : 'logged'}, MEMORY.md: ${memLines.out} lines` }
    },
    'list-crons': async () => {
      const r = await run('ls ~/.openclaw/crons/ 2>/dev/null || echo "no crons dir"')
      return { summary: 'Cron files', details: { crons: r.out || 'no crons dir' } }
    },
    'openclaw-status': async () => {
      const [procs, gateway] = await Promise.all([
        run('ps aux | grep "[o]penclaw" | grep -v grep'),
        run('ps aux | grep "[o]penclaw-gateway" | grep -v grep'),
      ])
      return { summary: `${gateway.out ? 'gateway running' : 'gateway down'} — ${procs.out ? procs.out.split('\n').length : 0} processes`, details: { processes: procs.out, gateway: gateway.out } }
    },
  }

  if (!actions[action]) {
    return res.status(400).json({ ok: false, error: `Unknown action: ${action}` })
  }

  try {
    const result = await Promise.race([
      actions[action](),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout (10s)')), 10000))
    ])
    res.json({ ok: true, id, ...result })
  } catch (e) {
    res.json({ ok: false, id, error: e.message })
  }
})

async function runBlogwatcherScan() {
  const scan = await run('blogwatcher scan 2>&1')
  await new Promise(r => setTimeout(r, 2000))
  const articles = await run('blogwatcher articles 2>&1')
  return [scan.out, articles.out].join('\n')
}

// SPA fallback
app.get('*', (req, res) => {
  if (!req.path.startsWith('/api')) {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'))
  } else {
    res.status(404).json({ error: 'not found' })
  }
})

app.listen(PORT, () => {
  console.log('🐾 Sig Botti OS running at http://localhost:5200')
})
