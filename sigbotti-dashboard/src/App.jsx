import React, { useEffect, useState, useRef, Suspense, useCallback } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// ─── Palette ──────────────────────────────────────────────────────────────────
const C = {
  bg: '#050508',
  panel: '#0a0a12',
  panelDark: '#07070f',
  border: '#1a1a2e',
  accent: '#00f5d4',
  accent2: '#f72585',
  accent3: '#9b5de5',
  text: '#c8c8e0',
  dim: '#4a4a6a',
  success: '#00f5a0',
  warning: '#f5a623',
  danger: '#f5365c',
}

// ─── API ───────────────────────────────────────────────────────────────────────
const API = '' // relative — proxied in dev, served from same origin in production

async function apiAction(action) {
  const r = await fetch(`${API}/api/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  })
  return r.json()
}

async function apiStatus() {
  try {
    const r = await fetch(`${API}/api/status`)
    return r.json()
  } catch {
    return null
  }
}

// ─── World ────────────────────────────────────────────────────────────────────

function GridFloor() {
  return (
    <gridHelper args={[40, 40, C.border, C.border]} position={[0, -2, 0]} />
  )
}

function SigCore() {
  const meshRef = useRef()
  const glowRef = useRef()

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.008
      meshRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
    if (glowRef.current) {
      const s = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.05
      glowRef.current.scale.set(s, s, s)
    }
  })

  return (
    <group position={[0, 0, 0]}>
      <mesh ref={glowRef}>
        <icosahedronGeometry args={[2.2, 1]} />
        <meshNormalMaterial transparent opacity={0.08} />
      </mesh>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[1.5, 0]} />
        <meshStandardMaterial
          color={C.accent}
          emissive={C.accent}
          emissiveIntensity={0.4}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>
      <mesh>
        <icosahedronGeometry args={[0.8, 0]} />
        <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={1} roughness={0} />
      </mesh>
    </group>
  )
}

function SystemBlock({ position, color, label, speed = 1, size = 0.6, pulseRef }) {
  const ref = useRef()

  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.x += 0.005 * speed
      ref.current.rotation.y += 0.008 * speed
      ref.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * speed + position[0]) * 0.3
    }
    if (pulseRef?.current) {
      pulseRef.current.rotation.y += 0.02 * speed
    }
  })

  return (
    <group position={position}>
      <mesh ref={ref}>
        <boxGeometry args={[size, size, size]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} roughness={0.3} metalness={0.6} />
      </mesh>
      {pulseRef && (
        <mesh ref={pulseRef} position={[0, 0, 0]}>
          <sphereGeometry args={[size * 0.6, 8, 8]} />
          <meshBasicMaterial color={color} transparent opacity={0.15} />
        </mesh>
      )}
    </group>
  )
}

function World({ activeBlock }) {
  const { camera } = useThree()
  const blockRefs = {
    HEART: useRef(), MEMORY: useRef(), SCANNER: useRef(), GIT: useRef(), CRON: useRef(),
  }

  useEffect(() => {
    camera.position.set(0, 8, 14)
    camera.lookAt(0, 0, 0)
  }, [camera])

  useFrame((state) => {
    // Pulse the active block
    const key = activeBlock
    if (key && blockRefs[key]?.current) {
      const s = 1 + Math.sin(state.clock.elapsedTime * 4) * 0.15
      blockRefs[key].current.scale.set(s, s, s)
    }
  })

  return (
    <>
      <color attach="background" args={[C.bg]} />
      <fog attach="fog" args={[C.bg, 20, 60]} />
      <ambientLight intensity={0.3} />
      <pointLight position={[0, 5, 0]} intensity={1} color={C.accent} distance={20} />
      <pointLight position={[5, 3, 5]} intensity={0.5} color={C.accent2} distance={15} />
      <pointLight position={[-5, 3, -5]} intensity={0.5} color={C.accent3} distance={15} />

      <GridFloor />
      <SigCore />

      <SystemBlock ref={blockRefs.HEART} position={[4, 1, 0]} color={C.accent} label="HEART" speed={1.2} size={0.7} />
      <SystemBlock ref={blockRefs.MEMORY} position={[-4, 0.5, 1]} color={C.accent2} label="MEM" speed={0.8} size={0.6} />
      <SystemBlock ref={blockRefs.SCANNER} position={[0, 2, -4]} color={C.accent3} label="SCAN" speed={1.5} size={0.5} />
      <SystemBlock ref={blockRefs.GIT} position={[-3, 1.5, -3]} color={C.warning} label="GIT" speed={0.6} size={0.55} />
      <SystemBlock ref={blockRefs.CRON} position={[3, 0.8, 3]} color={C.success} label="CRON" speed={1.0} size={0.65} />

      <OrbitControls enablePan={false} minDistance={6} maxDistance={30} maxPolarAngle={Math.PI / 2.1} autoRotate autoRotateSpeed={0.4} />
    </>
  )
}

// ─── Panel primitives ──────────────────────────────────────────────────────────

function Panel({ title, children, accent = C.accent, style }) {
  return (
    <div style={{
      background: C.panel,
      border: `1px solid ${C.border}`,
      borderTop: `2px solid ${accent}`,
      borderRadius: 4,
      padding: '10px 12px',
      display: 'flex',
      flexDirection: 'column',
      gap: 7,
      minWidth: 0,
      ...style,
    }}>
      <div style={{ color: accent, fontSize: 9, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 2 }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function StatRow({ label, value, color = C.text, small }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: small ? 10 : 11, minWidth: 0 }}>
      <span style={{ color: C.dim, flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis' }}>{label}</span>
      <span style={{ color, fontWeight: 'bold', marginLeft: 8, flexShrink: 0 }}>{value}</span>
    </div>
  )
}

function StatusDot({ color = C.success, large }) {
  return (
    <span style={{
      display: 'inline-block',
      width: large ? 8 : 6,
      height: large ? 8 : 6,
      borderRadius: '50%',
      background: color,
      boxShadow: `0 0 6px ${color}`,
      marginRight: 6,
      verticalAlign: 'middle',
      flexShrink: 0,
    }} />
  )
}

function PulseBar({ value = 1, color = C.accent }) {
  return (
    <div style={{ background: C.border, borderRadius: 2, height: 3, overflow: 'hidden' }}>
      <div style={{
        width: `${Math.min(100, value * 100)}%`,
        height: '100%',
        background: color,
        boxShadow: `0 0 6px ${color}`,
        transition: 'width 0.5s ease',
      }} />
    </div>
  )
}

// ─── Action Buttons ────────────────────────────────────────────────────────────

function ActionBtn({ label, onClick, loading, accent = C.accent, icon }) {
  const [hover, setHover] = useState(false)
  const [pressed, setPressed] = useState(false)

  return (
    <button
      onClick={onClick}
      disabled={loading}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => { setHover(false); setPressed(false) }}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      style={{
        background: loading ? `${accent}15` : pressed ? `${accent}30` : hover ? `${accent}22` : 'transparent',
        border: `1px solid ${loading ? accent + '40' : hover ? accent : C.border}`,
        color: loading ? accent + 'aa' : hover ? accent : C.text,
        padding: '5px 8px',
        borderRadius: 3,
        fontSize: 10,
        fontFamily: 'inherit',
        cursor: loading ? 'not-allowed' : 'pointer',
        textAlign: 'left',
        transition: 'all 0.12s',
        marginBottom: 3,
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        opacity: pressed ? 0.8 : 1,
      }}
    >
      {loading ? '⏳' : icon || '▶'} {label}
    </button>
  )
}

// ─── Output Log ────────────────────────────────────────────────────────────────

function OutputLog({ entries }) {
    const bottomRef = useRef(null)
    useEffect(() => {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [entries])

    return (
      <div style={{
        borderTop: `1px solid ${C.border}`,
        background: `${C.panelDark}f0`,
        flex: 1,
        overflowY: 'auto',
        padding: '8px 12px',
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
        minHeight: 0,
      }}>
        {entries.length === 0 && (
          <div style={{ color: C.dim, fontSize: 10, fontStyle: 'italic' }}>
            Action output will appear here...
          </div>
        )}
        {entries.map((e, i) => (
          <div key={i} style={{ fontSize: 10, lineHeight: 1.5 }}>
            <span style={{ color: C.dim, marginRight: 8 }}>{e.time}</span>
            <span style={{
              color: e.type === 'ok' ? C.success : e.type === 'err' ? C.danger : e.type === 'info' ? C.accent : C.text,
              fontWeight: 'bold',
              marginRight: 8,
            }}>[{e.type.toUpperCase()}]</span>
            <span style={{ color: C.text }}>{e.msg}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    )
}

// ─── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [tick, setTick] = useState(0)
  const [status, setStatus] = useState(null)
  const [activeBlock, setActiveBlock] = useState(null)
  const [loading, setLoading] = useState({})
  const [logEntries, setLogEntries] = useState([])
  const [expanded, setExpanded] = useState(true)
  const time = new Date().toLocaleTimeString('en-US', { timeZone: 'America/New_York' })
  const date = new Date().toLocaleDateString('en-US', { timeZone: 'America/New_York', weekday: 'short', month: 'short', day: 'numeric' })

  const addLog = useCallback((msg, type = 'info') => {
    const t = new Date().toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour12: false })
    setLogEntries(prev => [...prev.slice(-50), { time: t, msg, type }])
  }, [])

  const doAction = useCallback(async (actionKey, label, blockKey) => {
    if (loading[actionKey]) return
    setLoading(prev => ({ ...prev, [actionKey]: true }))
    setActiveBlock(blockKey)
    addLog(`Starting: ${label}`, 'info')

    try {
      const result = await apiAction(actionKey)
      if (result.ok) {
        addLog(`✓ ${result.summary || label}`, 'ok')
        if (result.details) {
          const d = result.details
          if (d.branch) addLog(`  branch: ${d.branch}`, 'text')
          if (d.status) addLog(`  ${d.status || '(clean)'}`, 'text')
          if (d.log) addLog(`  ${d.log.split('\n').join('\n  ')}`, 'text')
          if (d.newArticles !== undefined) addLog(`  ${d.newArticles} new articles`, 'text')
          if (d.crons) {
            d.crons.split('\n').filter(l => l.trim()).forEach(l => addLog(`  ${l.trim()}`, 'text'))
          }
          if (d.output) addLog(`  ${d.output}`, 'text')
          if (d.scan) {
            const newCount = (d.scan.match(/New: \d+/g) || []).join(', ')
            if (newCount) addLog(`  ${newCount}`, 'text')
          }
        }
      } else {
        addLog(`✗ ${result.error || 'Failed'}`, 'err')
      }
    } catch (e) {
      addLog(`✗ ${e.message}`, 'err')
    } finally {
      setLoading(prev => ({ ...prev, [actionKey]: false }))
      setActiveBlock(null)
      setTick(t => t + 1)
    }
  }, [loading, addLog])

  // Periodic status refresh
  useEffect(() => {
    const id = setInterval(async () => {
      const s = await apiStatus()
      if (s) setStatus(s)
    }, 15000)
    return () => clearInterval(id)
  }, [])

  // Initial status load
  useEffect(() => {
    apiStatus().then(s => { if (s) setStatus(s) })
  }, [])

  // Clock tick
  useEffect(() => {
    const id = setInterval(() => setTick(t => t + 1), 1000)
    return () => clearInterval(id)
  }, [])

  const actions = [
    { key: 'refresh', label: 'Refresh heartbeat', icon: '🔄', block: 'HEART' },
    { key: 'scan-rss', label: 'Scan RSS feeds', icon: '🔍', block: 'SCANNER' },
    { key: 'git-status', label: 'Git status', icon: '📁', block: 'GIT' },
    { key: 'run-scanner', label: 'Run scanner now', icon: '📊', block: 'SCANNER' },
    { key: 'sync-memory', label: 'Sync memory', icon: '🧠', block: 'MEMORY' },
    { key: 'list-crons', label: 'List crons', icon: '⏱', block: 'CRON' },
    { key: 'openclaw-status', label: 'OpenClaw status', icon: '⚙', block: 'HEART' },
  ]

  return (
    <div style={{
      width: '100vw', height: '100vh',
      background: C.bg,
      display: 'flex',
      flexDirection: 'column',
      color: C.text,
      overflow: 'hidden',
    }}>
      {/* ── Header ─────────────────────────────────────────────── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '8px 16px',
        borderBottom: `1px solid ${C.border}`,
        background: `${C.panel}ee`,
        flexShrink: 0,
        zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ fontSize: 20 }}>🐾</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 'bold', color: C.accent, letterSpacing: 2 }}>SIGBOTTI OS</div>
            <div style={{ fontSize: 9, color: C.dim, letterSpacing: 1 }}>AUTONOMOUS AGI CORE</div>
          </div>
        </div>

        {/* System status dots */}
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          {[
            { label: 'OC', ok: true },
            { label: 'GW', ok: true },
            { label: 'OLL', ok: true },
            { label: 'BLOG', ok: true },
          ].map(({ label, ok }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 9 }}>
              <StatusDot color={ok ? C.success : C.danger} />
              <span style={{ color: C.dim }}>{label}</span>
            </div>
          ))}
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 11, color: C.text }}>{date}</div>
          <div style={{ fontSize: 11, color: C.accent, fontVariantNumeric: 'tabular-nums' }}>{time}</div>
        </div>
      </div>

      {/* ── Main ──────────────────────────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

        {/* ── Left panels ─────────────────────────────────────── */}
        <div style={{
          width: 220,
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          padding: 10,
          overflowY: 'auto',
          borderRight: `1px solid ${C.border}`,
          flexShrink: 0,
        }}>
          <Panel title="❤️ Heartbeat" accent={C.accent}>
            <StatRow label="Status" value="ACTIVE" color={C.success} />
            <StatRow label="Interval" value="30 min" />
            <PulseBar value={0.82} color={C.accent} />
            <StatRow label="RSS feeds" value="5" />
            <StatRow label="New articles" value="2 unread" color={C.warning} />
            <StatRow label="Last scan" value={time} small />
          </Panel>

          <Panel title="🧠 Memory" accent={C.accent2}>
            <StatRow label="Long-term" value="MEMORY.md" />
            <StatRow label="Hot RAM" value="SESSION" />
            <StatRow label="Daily logs" value="14 days" />
            <StatRow label="Vector store" value="active" color={C.success} />
            <StatRow label="Learnings" value="~20" />
          </Panel>

          <Panel title="🔍 Scanner" accent={C.accent3}>
            <StatRow label="Universe" value="43 stocks" />
            <StatRow label="Last run" value="midnight" color={C.dim} />
            <StatRow label="Next run" value="midnight ET" color={C.accent} />
            <StatRow label="Last signals" value="21 found" color={C.success} />
          </Panel>

          <Panel title="⏱ Crons" accent={C.warning}>
            <StatRow label="Self-review" value="9:00 AM ET" />
            <StatRow label="Scanner" value="midnight ET" />
            <StatRow label="Backup" value="hourly" />
            <StatRow label="Self-eval" value="~21d" color={C.dim} />
          </Panel>

          <Panel title="🐾 Agent" accent={C.accent}>
            <StatRow label="Model" value="MiniMax-M2" />
            <StatRow label="Benchmark" value="3.1 / 5" color={C.warning} />
            <StatRow label="Skills" value="~30" />
            <StatRow label="Session" value="main" />
          </Panel>
        </div>

        {/* ── World viewport ──────────────────────────────────── */}
        <div style={{ flex: 1, position: 'relative', minWidth: 0 }}>
          <Canvas gl={{ antialias: true, powerPreference: 'high-performance' }} style={{ position: 'absolute', inset: 0 }}>
            <Suspense fallback={null}>
              <World activeBlock={activeBlock} />
            </Suspense>
          </Canvas>

          {/* Module legend */}
          <div style={{
            position: 'absolute', top: 10, right: 10,
            background: `${C.panel}cc`,
            border: `1px solid ${C.border}`,
            borderRadius: 4,
            padding: '8px 10px',
            display: 'flex',
            flexDirection: 'column',
            gap: 5,
          }}>
            {[
              { label: 'HEART', color: C.accent },
              { label: 'MEMORY', color: C.accent2 },
              { label: 'SCANNER', color: C.accent3 },
              { label: 'CRON', color: C.success },
              { label: 'GIT', color: C.warning },
            ].map(({ label, color }) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 9, letterSpacing: 1 }}>
                <StatusDot color={activeBlock === label ? color : color + '80'} large />
                <span style={{ color: activeBlock === label ? color : C.dim }}>{label}</span>
              </div>
            ))}
          </div>

          <div style={{
            position: 'absolute', bottom: 10, left: 12,
            fontSize: 9, color: C.dim, letterSpacing: 1,
          }}>
            DRAG TO ORBIT · SCROLL TO ZOOM
          </div>

          {/* Active block glow */}
          {activeBlock && (
            <div style={{
              position: 'absolute', top: 10, left: 12,
              fontSize: 10, color: C.accent,
              letterSpacing: 1,
              animation: 'pulse 1s ease-in-out infinite',
              background: `${C.panel}88`,
              padding: '4px 8px',
              borderRadius: 3,
              border: `1px solid ${C.accent}40`,
            }}>
              ⚡ {activeBlock} ACTIVE
            </div>
          )}
        </div>

        {/* ── Right panels ────────────────────────────────────── */}
        <div style={{
          width: 220,
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          padding: 10,
          overflowY: 'auto',
          borderLeft: `1px solid ${C.border}`,
          flexShrink: 0,
        }}>
          <Panel title="⚡ Actions" accent={C.warning}>
            {actions.map(a => (
              <ActionBtn
                key={a.key}
                label={a.label}
                icon={a.icon}
                loading={!!loading[a.key]}
                accent={C.warning}
                onClick={() => doAction(a.key, a.label, a.block)}
              />
            ))}
          </Panel>

          <Panel title="⚙ Systems" accent={C.dim}>
            <StatRow label="OpenClaw" value="running" color={C.success} />
            <StatRow label="Gateway" value="online" color={C.success} />
            <StatRow label="Ollama" value="connected" color={C.success} />
            <StatRow label="Blogwatcher" value="active" color={C.success} />
            <StatRow label="PerfectPlace" value="ok" color={C.success} />
          </Panel>

          {/* Output log */}
          <Panel title="📋 Output Log" accent={C.accent3} style={{ flex: 1, minHeight: 120 }}>
            <OutputLog entries={logEntries} />
          </Panel>
        </div>
      </div>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <div style={{
        padding: '5px 16px',
        borderTop: `1px solid ${C.border}`,
        background: `${C.panel}cc`,
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: 9,
        color: C.dim,
        flexShrink: 0,
        letterSpacing: 1,
      }}>
        <span>🐾 SIGBOTTI OS — Autonomous AGI Control Interface</span>
        <span>TICK #{tick}</span>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${C.border}; border-radius: 2px; }
      `}</style>
    </div>
  )
}
