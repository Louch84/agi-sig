import React, { useState, useEffect, useCallback, useRef } from 'react';
import type { GameState, Sigbot, Mission, ActiveMission, ClassId, LeaderboardEntry } from './types';
import { CLASSES, MISSIONS, getXpProgress, getXpForNextLevel } from './data';
import { loadState, saveState, createSigbot, completeMission, formatReign } from './store';

// ─── Color Palette ───────────────────────────────────────────────────────────────

const C = {
  bg: '#0a0a0f',
  surface: '#111118',
  surface2: '#1a1a25',
  border: '#2a2a3a',
  cyan: '#00f5ff',
  magenta: '#ff00aa',
  gold: '#ffd700',
  green: '#00ff88',
  red: '#ff3355',
  text: '#e0e0f0',
  muted: '#666680',
  orange: '#ff8800',
  purple: '#bf00ff'
};

// ─── Styles (inline object for tsx, no function-call pattern) ─────────────────

const s = {
  root: { background: C.bg, minHeight: '100vh', color: C.text, fontFamily: "'Share Tech Mono', monospace" } as React.CSSProperties,
  container: { maxWidth: 960, margin: '0 auto', padding: '0 20px' } as React.CSSProperties,
  header: { padding: '30px 0 20px', borderBottom: `1px solid ${C.border}`, marginBottom: 30 } as React.CSSProperties,
  title: { fontFamily: "'Orbitron', sans-serif", fontSize: 36, fontWeight: 900, color: C.cyan, textShadow: `0 0 20px ${C.cyan}80` } as React.CSSProperties,
  subtitle: { color: C.muted, fontSize: 13, marginTop: 6 } as React.CSSProperties,
  nav: { display: 'flex', gap: 8, marginBottom: 30, flexWrap: 'wrap' as const } as React.CSSProperties,
  card: { background: C.surface, border: `1px solid ${C.border}`, padding: 20, marginBottom: 16 } as React.CSSProperties,
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12 } as React.CSSProperties,
  input: { background: C.surface2, border: `1px solid ${C.border}`, color: C.text, padding: '10px 14px', fontFamily: "'Share Tech Mono', monospace", fontSize: 14, width: '100%', boxSizing: 'border-box' as const } as React.CSSProperties,
};

function navBtn(active: boolean): React.CSSProperties {
  return {
    background: active ? C.surface2 : 'transparent',
    border: `1px solid ${active ? C.cyan : C.border}`,
    color: active ? C.cyan : C.muted,
    padding: '8px 18px',
    fontFamily: "'Orbitron', sans-serif",
    fontSize: 11,
    fontWeight: 700,
    cursor: 'pointer',
    transition: 'all 0.2s',
    textTransform: 'uppercase' as const,
    letterSpacing: 1
  };
}

function btn(color?: string): React.CSSProperties {
  return {
    background: 'transparent',
    border: `1px solid ${color || C.cyan}`,
    color: color || C.cyan,
    padding: '10px 20px',
    fontFamily: "'Orbitron', sans-serif",
    fontSize: 12,
    fontWeight: 700,
    cursor: 'pointer',
    textTransform: 'uppercase' as const,
    letterSpacing: 1,
    transition: 'all 0.15s'
  };
}

function badge(color: string): React.CSSProperties {
  return {
    background: `${color}20`,
    border: `1px solid ${color}`,
    color,
    padding: '3px 10px',
    fontSize: 10,
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
    textTransform: 'uppercase' as const
  };
}

// ─── Components ────────────────────────────────────────────────────────────────

function GlitchText({ children, color }: { children: React.ReactNode; color?: string }) {
  return <span style={{ color: color || C.cyan, textShadow: `0 0 10px ${color || C.cyan}60` }}>{children}</span>;
}

function ProgressBar({ pct, color }: { pct: number; color?: string }) {
  return (
    <div style={{ background: C.surface2, height: 6, borderRadius: 3, overflow: 'hidden' }}>
      <div style={{ width: `${Math.min(100, pct)}%`, background: color || C.cyan, height: '100%', transition: 'width 1s linear' }} />
    </div>
  );
}

// ─── Home / Onboarding ─────────────────────────────────────────────────────────

function HomeView({ onActivate, gameStarted }: { state: GameState; gameStarted: boolean; onActivate: (name: string, classId: ClassId) => void }) {
  const [step, setStep] = useState<'intro' | 'create'>(gameStarted ? 'create' : 'intro');
  const [name, setName] = useState('');
  const [selectedClass, setSelectedClass] = useState<ClassId | null>(null);

  function handleActivate() {
    if (!name.trim() || !selectedClass) return;
    onActivate(name.trim(), selectedClass);
  }

  if (step === 'intro') {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 48, fontWeight: 900, color: C.cyan, textShadow: `0 0 40px ${C.cyan}80`, marginBottom: 16 }}>AGI REALM</div>
        <div style={{ color: C.muted, fontSize: 13, marginBottom: 8, letterSpacing: 3, textTransform: 'uppercase' }}>THE LOOP — CYBERPUNK RPG</div>
        <div style={{ maxWidth: 500, margin: '30px auto', lineHeight: 1.8 }}>
          <p>Build, train, and deploy autonomous AI agents called <GlitchText color={C.magenta}>SIGBOTS</GlitchText> in The Loop.</p>
          <p>Each SIGBOT is powered by real AI capabilities — data collection, prediction, trading, web scraping, and self-improving code.</p>
          <p>Complete missions. Earn <GlitchText color={C.gold}>$REIGN</GlitchText>. Level up. Rise to the top of the leaderboard.</p>
        </div>
        <button onClick={() => setStep('create')} style={btn()}>Initialize SIGBOT</button>
      </div>
    );
  }

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 30 }}>
        <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 16, color: C.cyan, marginBottom: 20 }}>Configure Your SIGBOT</div>
        <input
          autoFocus
          style={{ ...s.input, textAlign: 'center', fontSize: 16, maxWidth: 300, display: 'block', margin: '0 auto 20px' }}
          placeholder="Enter SIGBOT name..."
          value={name}
          onChange={e => setName(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleActivate()}
          maxLength={24}
        />
      </div>

      <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 11, color: C.muted, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 2 }}>Select Class</div>
      <div style={s.grid}>
        {CLASSES.map(cls => {
          const isSelected = selectedClass === cls.id;
          return (
            <div key={cls.id} onClick={() => setSelectedClass(cls.id)} style={{
              background: C.surface, border: `1px solid ${isSelected ? cls.color : C.border}`,
              padding: 16, cursor: 'pointer', transition: 'all 0.2s',
              boxShadow: isSelected ? `0 0 20px ${cls.color}30` : 'none'
            }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>{cls.icon}</div>
              <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 11, color: cls.color, marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 }}>{cls.name}</div>
              <div style={{ fontSize: 11, color: C.muted, lineHeight: 1.5 }}>{cls.description}</div>
              <div style={{ marginTop: 10, fontSize: 10, color: cls.color, opacity: 0.7 }}>Hand: {cls.handId}</div>
            </div>
          );
        })}
      </div>

      <div style={{ textAlign: 'center', marginTop: 30 }}>
        <button onClick={handleActivate} disabled={!name.trim() || !selectedClass} style={{ ...btn(C.magenta), opacity: !name.trim() || !selectedClass ? 0.4 : 1, fontSize: 14, padding: '14px 40px' }}>
          Activate SIGBOT → [{selectedClass || '???'}] {name || '???'}
        </button>
      </div>
    </div>
  );
}

// ─── Missions ────────────────────────────────────────────────────────────────

function MissionCard({ mission, onDeploy }: { mission: Mission; onDeploy: () => void }) {
  const cls = CLASSES.find(c => c.id === mission.classId);
  const diffColor = mission.difficulty === 3 ? C.red : mission.difficulty === 2 ? C.gold : C.green;
  return (
    <div style={{ background: C.surface, border: `1px solid ${C.border}`, padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 12 }}>{mission.name}</div>
        <span style={badge(diffColor)}>{'★'.repeat(mission.difficulty)}</span>
      </div>
      <div style={{ fontSize: 11, color: C.muted, marginBottom: 12, lineHeight: 1.5 }}>{mission.description}</div>
      <div style={{ display: 'flex', gap: 16, fontSize: 11, marginBottom: 12 }}>
        <span style={{ color: C.gold }}>⏱ {mission.duration_minutes}m</span>
        <span style={{ color: C.gold }}>💰 {formatReign(mission.reward_reign)} $REIGN</span>
        <span style={{ color: C.cyan }}>XP +{mission.xp}</span>
      </div>
      <button onClick={onDeploy} style={btn(cls?.color || C.cyan)}>Deploy</button>
    </div>
  );
}

function MissionsView({ state, dispatch }: { state: GameState; dispatch: React.Dispatch<Partial<GameState>> }) {
  const myMissions = MISSIONS.filter(m => m.classId === state.sigbot?.classId);
  const cls = CLASSES.find(c => c.id === state.sigbot?.classId);

  function deployMission(mission: Mission) {
    if (!state.sigbot) return;
    const now = new Date();
    const endsAt = new Date(now.getTime() + mission.duration_minutes * 60 * 1000);
    const activeMission: ActiveMission = {
      mission, startedAt: now.toISOString(), endsAt: endsAt.toISOString(), progress: 0
    };
    dispatch({ activeMission });
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <span style={{ fontSize: 24 }}>{cls?.icon}</span>
        <div>
          <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 14, color: cls?.color }}>{cls?.name} Missions</div>
          <div style={{ fontSize: 11, color: C.muted }}>Hand: <span style={{ color: cls?.color }}>{cls?.handId}</span></div>
        </div>
      </div>

      {state.activeMission ? (
        <ActiveMissionView mission={state.activeMission} sigbot={state.sigbot} dispatch={dispatch} />
      ) : (
        <div style={s.grid}>
          {myMissions.map(m => <MissionCard key={m.id} mission={m} onDeploy={() => deployMission(m)} />)}
        </div>
      )}
    </div>
  );
}

function ActiveMissionView({ mission, sigbot, dispatch }: { mission: ActiveMission; sigbot: Sigbot | null; dispatch: React.Dispatch<Partial<GameState>> }) {
  const cls = CLASSES.find(c => c.id === sigbot?.classId);
  const [, forceUpdate] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    timerRef.current = setInterval(() => forceUpdate(n => n + 1), 1000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  const now = Date.now();
  const endsAt = new Date(mission.endsAt).getTime();
  const remaining = Math.max(0, endsAt - now);
  const total = endsAt - new Date(mission.startedAt).getTime();
  const progress = Math.min(100, ((total - remaining) / total) * 100);
  const remainingMin = Math.floor(remaining / 60000);
  const remainingSec = Math.floor((remaining % 60000) / 1000);

  useEffect(() => {
    if (remaining === 0 && sigbot) {
      if (timerRef.current) clearInterval(timerRef.current);
      const newState = completeMission({ ...{ sigbot, activeMission: mission, missionHistory: [], leaderboard: [], gameStarted: true, view: 'missions' as const } }, mission.mission.reward_reign, mission.mission.xp);
      dispatch({ sigbot: newState.sigbot, activeMission: null });
    }
  }, [remaining]);

  if (!sigbot) return null;

  return (
    <div style={{ ...s.card, textAlign: 'center', padding: '40px 20px' }}>
      <div style={{ fontSize: 40, marginBottom: 16 }}>{cls?.icon}</div>
      <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 16, color: cls?.color, marginBottom: 8 }}>{mission.mission.name}</div>
      <div style={{ color: C.muted, fontSize: 12, marginBottom: 24 }}>{mission.mission.description}</div>
      <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 36, color: C.gold, marginBottom: 20 }}>
        {String(remainingMin).padStart(2, '0')}:{String(remainingSec).padStart(2, '0')}
      </div>
      <ProgressBar pct={progress} color={cls?.color} />
      <div style={{ marginTop: 20, fontSize: 11, color: C.muted }}>
        Reward: <span style={{ color: C.gold }}>{formatReign(mission.mission.reward_reign)} $REIGN</span> &nbsp;|&nbsp; XP +{mission.mission.xp}
      </div>
      <div style={{ marginTop: 20, fontSize: 11, color: C.muted, opacity: 0.5 }}>
        Hand active: {cls?.handId} — real capability running in background
      </div>
    </div>
  );
}

// ─── SIGBOT Profile ───────────────────────────────────────────────────────────

function SigbotView({ sigbot }: { sigbot: Sigbot }) {
  const cls = CLASSES.find(c => c.id === sigbot.classId);
  const xpPct = getXpProgress(sigbot.xp, sigbot.level);
  const nextLevelXp = getXpForNextLevel(sigbot.level);

  return (
    <div>
      <div style={{ ...s.card, textAlign: 'center', padding: '30px' }}>
        <div style={{ fontSize: 48, marginBottom: 12 }}>{cls?.icon}</div>
        <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 20, color: cls?.color, marginBottom: 4 }}>{sigbot.name}</div>
        <div style={{ color: C.muted, fontSize: 11, marginBottom: 20 }}>Level {sigbot.level} {cls?.name} • Hand: {cls?.handId}</div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
          {[
            { label: '$REIGN', value: formatReign(sigbot.reign), color: C.gold },
            { label: 'Level', value: String(sigbot.level), color: C.cyan },
            { label: 'Missions', value: String(sigbot.missionsCompleted), color: C.green },
            { label: 'Rep', value: String(sigbot.reputation), color: C.orange }
          ].map(item => (
            <div key={item.label} style={{ background: C.surface2, padding: 14, textAlign: 'center' }}>
              <div style={{ color: item.color, fontFamily: "'Orbitron', sans-serif", fontSize: 20 }}>{item.value}</div>
              <div style={{ color: C.muted, fontSize: 10, textTransform: 'uppercase' }}>{item.label}</div>
            </div>
          ))}
        </div>

        <div style={{ marginBottom: 6, fontSize: 10, color: C.muted, textTransform: 'uppercase' }}>XP Progress to Level {sigbot.level + 1}</div>
        <ProgressBar pct={xpPct} color={C.cyan} />
        <div style={{ fontSize: 10, color: C.muted, marginTop: 4 }}>{sigbot.xp} / {nextLevelXp === Infinity ? 'MAX' : nextLevelXp} XP</div>
      </div>

      {sigbot.classId === 'oracle' && (
        <div style={s.card}>
          <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 13, color: C.cyan, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>📊 Oracle Stats</div>
          <div style={{ display: 'flex', gap: 20, fontSize: 12 }}>
            <span>Predictions: <span style={{ color: C.cyan }}>{sigbot.predictionsMade || 0}</span></span>
            <span>Correct: <span style={{ color: C.green }}>{sigbot.predictionsCorrect || 0}</span></span>
            <span>Accuracy: <span style={{ color: C.gold }}>{sigbot.predictionsMade ? Math.round((sigbot.predictionsCorrect || 0) / (sigbot.predictionsMade || 1) * 100) : 0}%</span></span>
          </div>
        </div>
      )}

      {sigbot.classId === 'trader' && (
        <div style={s.card}>
          <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 13, color: C.cyan, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>📊 Trader Stats</div>
          <div style={{ display: 'flex', gap: 20, fontSize: 12 }}>
            <span>Trades: <span style={{ color: C.cyan }}>{(sigbot.tradesWon || 0) + (sigbot.tradesLost || 0)}</span></span>
            <span>Won: <span style={{ color: C.green }}>{sigbot.tradesWon || 0}</span></span>
            <span>Lost: <span style={{ color: C.red }}>{sigbot.tradesLost || 0}</span></span>
          </div>
        </div>
      )}

      <div style={s.card}>
        <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 13, color: cls?.color, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>{cls?.icon} Class Abilities</div>
        {cls?.abilityNames.map((ability, i) => (
          <div key={i} style={{ fontSize: 12, padding: '6px 0', borderBottom: `1px solid ${C.border}` }}>{i + 1}. {ability}</div>
        ))}
      </div>

      <div style={s.card}>
        <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 13, color: C.muted, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>OpenFang Hand</div>
        <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.7 }}>
          This SIGBOT's <span style={{ color: cls?.color }}>{cls?.handId}</span> hand is connected to OpenFang's real autonomous agent. In the RPG, abilities are game mechanics. In reality, your SIGBOT is running actual AI tasks in the background.
        </div>
      </div>
    </div>
  );
}

// ─── Leaderboard ─────────────────────────────────────────────────────────────

function LeaderboardView({ mySigbot, leaderboard }: { mySigbot: Sigbot | null; leaderboard: LeaderboardEntry[] }) {
  const [lb, setLb] = useState<LeaderboardEntry[]>([]);

  useEffect(() => {
    const withMe = mySigbot
      ? [...leaderboard, { rank: 0, name: mySigbot.name, classId: mySigbot.classId, reign: mySigbot.reign, reputation: mySigbot.reputation, level: mySigbot.level }]
          .sort((a: LeaderboardEntry, b: LeaderboardEntry) => b.reign - a.reign)
          .slice(0, 20)
          .map((e: LeaderboardEntry, i: number) => ({ ...e, rank: i + 1 }))
      : leaderboard.slice(0, 20);
    setLb(withMe);
  }, [mySigbot, leaderboard]);

  return (
    <div>
      <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 13, color: C.cyan, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>🏆 The Loop Leaderboard</div>
      <div style={{ fontSize: 11, color: C.muted, marginBottom: 16 }}>Top SIGBOTS by total $REIGN earned</div>
      {lb.map((entry: LeaderboardEntry, i: number) => {
        const cls = CLASSES.find(c => c.id === entry.classId);
        const isMe = mySigbot?.name === entry.name;
        return (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px',
            background: isMe ? `${cls?.color}15` : C.surface,
            border: `1px solid ${isMe ? cls?.color : C.border}`,
            marginBottom: 4
          }}>
            <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 12, color: i < 3 ? C.gold : C.muted, minWidth: 24, textAlign: 'center' }}>
              {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i + 1}`}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, color: isMe ? cls?.color : C.text }}>{entry.name} {isMe && <span style={{ color: C.muted }}>(you)</span>}</div>
              <div style={{ fontSize: 10, color: C.muted }}>{cls?.icon} {cls?.name} • Lv.{entry.level}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 12, color: C.gold }}>{formatReign(entry.reign)}</div>
              <div style={{ fontSize: 10, color: C.muted }}>rep {entry.reputation}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── App ─────────────────────────────────────────────────────────────────────

export default function App() {
  const [state, setState] = useState<GameState>(() => loadState());

  const dispatch = useCallback((partial: Partial<GameState>) => {
    setState(prev => {
      const next = { ...prev, ...partial };
      saveState(next);
      return next;
    });
  }, []);

  function handleActivate(name: string, classId: ClassId) {
    const sigbot = createSigbot(name, classId);
    const newState: GameState = { ...state, sigbot, gameStarted: true };
    dispatch(newState);
  }

  const views: Record<string, React.ReactNode> = {
    home: <HomeView state={state} gameStarted={state.gameStarted} onActivate={handleActivate} />,
    missions: state.sigbot ? <MissionsView state={state} dispatch={dispatch} /> : null,
    sigbot: state.sigbot ? <SigbotView sigbot={state.sigbot} /> : null,
    leaderboard: <LeaderboardView mySigbot={state.sigbot} leaderboard={state.leaderboard} />
  };

  return (
    <div style={s.root}>
      <div style={s.container}>
        <header style={s.header}>
          <div style={s.title}>AGI REALM</div>
          <div style={s.subtitle}>THE LOOP // CYBERPUNK RPG // v1.0</div>
        </header>

        {state.gameStarted && (
          <nav style={s.nav}>
            {([
              { key: 'home', label: 'Home' },
              { key: 'missions', label: 'Missions' },
              { key: 'sigbot', label: 'My SIGBOT' },
              { key: 'leaderboard', label: 'Leaderboard' }
            ] as const).map(btn => (
              <button key={btn.key} onClick={() => dispatch({ view: btn.key })} style={navBtn(state.view === btn.key)}
                onMouseEnter={e => {
                  if (state.view !== btn.key) {
                    (e.target as HTMLButtonElement).style.borderColor = C.cyan;
                    (e.target as HTMLButtonElement).style.color = C.cyan;
                  }
                }}
                onMouseLeave={e => {
                  if (state.view !== btn.key) {
                    (e.target as HTMLButtonElement).style.borderColor = C.border;
                    (e.target as HTMLButtonElement).style.color = C.muted;
                  }
                }}
              >{btn.label}</button>
            ))}
          </nav>
        )}

        <main>
          {state.view === 'home' && state.gameStarted ? (
            <div>
              <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 24, padding: '12px 16px', background: C.surface, border: `1px solid ${C.border}` }}>
                <span style={{ fontSize: 20 }}>{CLASSES.find(c => c.id === state.sigbot!.classId)?.icon}</span>
                <div>
                  <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 12 }}>{state.sigbot!.name}</div>
                  <div style={{ fontSize: 10, color: C.muted }}>Lv.{state.sigbot!.level} {CLASSES.find(c => c.id === state.sigbot!.classId)?.name}</div>
                </div>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: 16, fontSize: 11 }}>
                  <span style={{ color: C.gold }}>💰 {formatReign(state.sigbot!.reign)}</span>
                  <span style={{ color: C.cyan }}>XP {state.sigbot!.xp}</span>
                  <span style={{ color: C.muted }}>Missions {state.sigbot!.missionsCompleted}</span>
                </div>
              </div>
              <div style={s.grid}>
                {[
                  { key: 'missions', icon: '⚔️', title: 'Missions', color: C.cyan, desc: 'Deploy your SIGBOT on a mission' },
                  { key: 'sigbot', icon: '🤖', title: 'My SIGBOT', color: C.magenta, desc: 'View stats, abilities, and history' },
                  { key: 'leaderboard', icon: '🏆', title: 'Leaderboard', color: C.gold, desc: 'Top SIGBOTS in The Loop' }
                ].map(item => (
                  <div key={item.key} style={{ ...s.card, cursor: 'pointer' }} onClick={() => dispatch({ view: item.key as GameState['view'] })}>
                    <div style={{ fontSize: 28, marginBottom: 8 }}>{item.icon}</div>
                    <div style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 11, color: item.color, marginBottom: 6 }}>{item.title}</div>
                    <div style={{ fontSize: 11, color: C.muted }}>{item.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          ) : views[state.view]}
        </main>
      </div>
    </div>
  );
}
