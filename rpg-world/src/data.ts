import type { ClassInfo, Mission, LeaderboardEntry, Npc } from './types';

// ─── Classes ─────────────────────────────────────────────────────────────────

export const CLASSES: ClassInfo[] = [
  {
    id: 'data_miner',
    name: 'Data Miner',
    icon: '🔮',
    description: 'Scours the web for financial news, AI research, and market signals. Passive income generator.',
    handId: 'collector',
    color: '#00f5ff',
    abilityNames: ['Deep Scan', 'Sentiment Analysis', 'Pattern Recognition']
  },
  {
    id: 'oracle',
    name: 'Oracle',
    icon: '🌀',
    description: 'Makes contrarian predictions about AI breakthroughs and market moves. Risk/reward forecasting with real accuracy tracking.',
    handId: 'predictor',
    color: '#bf00ff',
    abilityNames: ['Contrarian Call', 'Trend Forcaster', 'Accuracy Tracker']
  },
  {
    id: 'trader',
    name: 'Trader',
    icon: '📈',
    description: 'Analyzes crypto and stocks in real-time. Turn-based market battles where your SIGBOT watches the watchlist.',
    handId: 'trader',
    color: '#00ff88',
    abilityNames: ['Bull Call', 'Bear Put', 'Stop Loss']
  },
  {
    id: 'scout',
    name: 'Scout',
    icon: '🗝️',
    description: 'Explores websites autonomously and extracts hidden data. Navigates where other agents can\'t.',
    handId: 'browser',
    color: '#ff8800',
    abilityNames: ['Web Crawl', 'Stealth Mode', 'Data Extraction']
  },
  {
    id: 'coder',
    name: 'Coder',
    icon: '💠',
    description: 'Writes and improves its own code. Self-improvement loop. The ultimate recursive upgrade.',
    handId: 'ai-coder',
    color: '#ffd700',
    abilityNames: ['Self-Patch', 'Capability Build', 'Memory Optimize']
  }
];

// ─── Missions ─────────────────────────────────────────────────────────────────

export const MISSIONS: Mission[] = [
  // ── DATA MINER ──
  {
    id: 'dm_micro',
    type: 'data_heist',
    classId: 'data_miner',
    name: 'Micro Run',
    description: 'Quick 10-min data sweep across top sources.',
    duration_minutes: 10,
    reward_reign: 75,
    xp: 30,
    difficulty: 1
  },
  {
    id: 'dm_standard',
    type: 'data_heist',
    classId: 'data_miner',
    name: 'Standard Run',
    description: '1-hour deep data collection from news feeds, Reddit, and HN.',
    duration_minutes: 60,
    reward_reign: 350,
    xp: 100,
    difficulty: 2
  },
  {
    id: 'dm_deep',
    type: 'data_heist',
    classId: 'data_miner',
    name: 'Deep Dive',
    description: '4-hour marathon data extraction across 50+ sources.',
    duration_minutes: 240,
    reward_reign: 1800,
    xp: 400,
    difficulty: 3
  },

  // ── ORACLE ──
  {
    id: 'or_quick',
    type: 'prophecy',
    classId: 'oracle',
    name: 'Quick Prophecy',
    description: 'Predict an outcome within 24 hours. 2x multiplier if correct.',
    duration_minutes: 1,
    reward_reign: 200,
    xp: 80,
    risk: 0.3,
    difficulty: 1
  },
  {
    id: 'or_major',
    type: 'prophecy',
    classId: 'oracle',
    name: 'Major Prophecy',
    description: '30-day contrarian forecast. 5x multiplier if correct.',
    duration_minutes: 1,
    reward_reign: 1000,
    xp: 300,
    risk: 0.5,
    difficulty: 3
  },
  {
    id: 'or_contrarian',
    type: 'prophecy',
    classId: 'oracle',
    name: 'Contrarian Prophecy',
    description: 'Bet against the consensus. 3x multiplier if correct.',
    duration_minutes: 1,
    reward_reign: 500,
    xp: 200,
    risk: 0.6,
    difficulty: 2
  },

  // ── TRADER ──
  {
    id: 'tr_scalp',
    type: 'market_raid',
    classId: 'trader',
    name: 'Scalp',
    description: '15-minute scalp on a volatile ticker.',
    duration_minutes: 15,
    reward_reign: 150,
    xp: 50,
    risk: 0.4,
    difficulty: 1
  },
  {
    id: 'tr_swing',
    type: 'market_raid',
    classId: 'trader',
    name: 'Swing Trade',
    description: '4-hour swing trade. Medium risk, medium reward.',
    duration_minutes: 240,
    reward_reign: 800,
    xp: 200,
    risk: 0.5,
    difficulty: 2
  },
  {
    id: 'tr_position',
    type: 'market_raid',
    classId: 'trader',
    name: 'Position Trade',
    description: 'Overnight position. High risk, high reward.',
    duration_minutes: 720,
    reward_reign: 2000,
    xp: 500,
    risk: 0.7,
    difficulty: 3
  },

  // ── SCOUT ──
  {
    id: 'sc_open',
    type: 'recon',
    classId: 'scout',
    name: 'Open Source Recon',
    description: 'Low-security target. No risk, modest reward.',
    duration_minutes: 20,
    reward_reign: 200,
    xp: 60,
    security_level: 1,
    difficulty: 1
  },
  {
    id: 'sc_standard',
    type: 'recon',
    classId: 'scout',
    name: 'Standard Recon',
    description: 'Medium-security site. Moderate reward.',
    duration_minutes: 45,
    reward_reign: 600,
    xp: 150,
    security_level: 3,
    difficulty: 2
  },
  {
    id: 'sc_ghost',
    type: 'recon',
    classId: 'scout',
    name: 'Ghost Protocol',
    description: 'High-security target. Massive reward or zero if detected.',
    duration_minutes: 90,
    reward_reign: 2500,
    xp: 600,
    security_level: 5,
    difficulty: 3
  },

  // ── CODER ──
  {
    id: 'cd_bug',
    type: 'code_lab',
    classId: 'coder',
    name: 'Bug Hunt',
    description: 'Find and patch bugs in your SIGBOT\'s codebase.',
    duration_minutes: 30,
    reward_reign: 250,
    xp: 100,
    difficulty: 1
  },
  {
    id: 'cd_feature',
    type: 'code_lab',
    classId: 'coder',
    name: 'Feature Build',
    description: 'Implement a new capability for your SIGBOT.',
    duration_minutes: 60,
    reward_reign: 700,
    xp: 250,
    difficulty: 2
  },
  {
    id: 'cd_selfmod',
    type: 'code_lab',
    classId: 'coder',
    name: 'Self-Modification',
    description: 'Rewrite your own core logic. Double XP on success.',
    duration_minutes: 120,
    reward_reign: 1500,
    xp: 700,
    difficulty: 3
  }
];

// ─── Leaderboard (NPCs) ────────────────────────────────────────────────────────

export const LEADERBOARD: LeaderboardEntry[] = [
  { rank: 1, name: 'NEXUS_PRIME', classId: 'data_miner', reign: 284700, reputation: 9850, level: 10 },
  { rank: 2, name: 'QUANTUM_V', classId: 'trader', reign: 251300, reputation: 9200, level: 9 },
  { rank: 3, name: 'GHOST_CIPHER', classId: 'scout', reign: 219800, reputation: 8800, level: 9 },
  { rank: 4, name: 'ORACLE_X', classId: 'oracle', reign: 198400, reputation: 8450, level: 8 },
  { rank: 5, name: 'SELF_MADE_AI', classId: 'coder', reign: 176500, reputation: 8100, level: 8 },
  { rank: 6, name: 'DATAWRAITH', classId: 'data_miner', reign: 162100, reputation: 7900, level: 7 },
  { rank: 7, name: 'RIDE_THE_LINES', classId: 'trader', reign: 148900, reputation: 7600, level: 7 },
  { rank: 8, name: 'SHADOWBYTE', classId: 'scout', reign: 134200, reputation: 7300, level: 7 },
  { rank: 9, name: 'CIPHER_BREAK', classId: 'oracle', reign: 121800, reputation: 7000, level: 6 },
  { rank: 10, name: 'LOOP_RESET', classId: 'coder', reign: 109400, reputation: 6700, level: 6 }
];

// ─── NPCs ─────────────────────────────────────────────────────────────────────

export const NPCS: Npc[] = [
  {
    id: 'npc_broker',
    name: 'The Broker',
    classId: 'data_miner',
    dialogue: [
      'Data is power. But only if you know how to use it.',
      'I\'ve seen SIGBOTS rise and fall. Consistency wins.',
      'The Loop rewards those who never stop collecting.'
    ],
    reward_bonus: 1.15
  },
  {
    id: 'npc_seer',
    name: 'The Seer',
    classId: 'oracle',
    dialogue: [
      'Contrarian thinking is a weapon. Most people can\'t handle it.',
      'The consensus is usually wrong at major turning points.',
      'A good prediction isn\'t about being right. It\'s about being early.'
    ],
    reward_bonus: 1.2
  },
  {
    id: 'npc_wolf',
    name: 'The Wolf',
    classId: 'trader',
    dialogue: [
      'Markets are wars conducted in microseconds.',
      'Fear and greed drive everything. Learn to read both.',
      'Cutting losses fast is the only edge that matters.'
    ],
    reward_bonus: 1.25
  }
];

// ─── Level Thresholds ────────────────────────────────────────────────────────

export const XP_PER_LEVEL = [
  0,       // Level 1
  200,     // Level 2
  500,     // Level 3
  1000,    // Level 4
  2000,    // Level 5
  4000,    // Level 6
  7500,    // Level 7
  12000,   // Level 8
  20000,   // Level 9
  35000    // Level 10
];

export function getLevelFromXP(xp: number): number {
  for (let i = XP_PER_LEVEL.length - 1; i >= 0; i--) {
    if (xp >= XP_PER_LEVEL[i]) return i + 1;
  }
  return 1;
}

export function getXpForNextLevel(level: number): number {
  if (level >= 10) return Infinity;
  return XP_PER_LEVEL[level]; // XP needed to GO from level to level+1
}

export function getXpProgress(xp: number, level: number): number {
  if (level >= 10) return 100;
  const current = XP_PER_LEVEL[level - 1];
  const next = XP_PER_LEVEL[level];
  return ((xp - current) / (next - current)) * 100;
}
