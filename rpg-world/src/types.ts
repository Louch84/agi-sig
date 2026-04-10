// ─── Core Types ────────────────────────────────────────────────────────────────

export type ClassId = 'data_miner' | 'oracle' | 'trader' | 'scout' | 'coder';

export type MissionType =
  | 'data_heist'
  | 'prophecy'
  | 'market_raid'
  | 'recon'
  | 'code_lab';

export interface ClassInfo {
  id: ClassId;
  name: string;
  icon: string;
  description: string;
  handId: string;
  color: string;
  abilityNames: string[];
}

export interface Mission {
  id: string;
  type: MissionType;
  classId: ClassId;
  name: string;
  description: string;
  duration_minutes: number;
  reward_reign: number;
  xp: number;
  risk?: number;
  security_level?: number;
  difficulty: 1 | 2 | 3;
}

export interface Sigbot {
  id: string;
  name: string;
  classId: ClassId;
  level: number;
  xp: number;
  reign: number;
  reputation: number;
  missionsCompleted: number;
  predictionsMade?: number;
  predictionsCorrect?: number;
  tradesWon?: number;
  tradesLost?: number;
  createdAt: string;
}

export interface LeaderboardEntry {
  rank: number;
  name: string;
  classId: ClassId;
  reign: number;
  reputation: number;
  level: number;
}

// ─── Chat Types ────────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: 'lou' | 'sigbotti';
  text: string;
  timestamp: string;
}

// ─── Game State ────────────────────────────────────────────────────────────────

export type ViewId = 'home' | 'missions' | 'sigbot' | 'leaderboard' | 'chat' | 'dashboard';

export interface GameState {
  sigbot: Sigbot | null;
  activeMission: ActiveMission | null;
  missionHistory: CompletedMission[];
  leaderboard: LeaderboardEntry[];
  gameStarted: boolean;
  view: ViewId;
  chatMessages: ChatMessage[];
  pendingBotReply: boolean;
}

export interface ActiveMission {
  mission: Mission;
  startedAt: string;
  endsAt: string;
  progress: number;
}

export interface CompletedMission {
  missionName: string;
  missionType: MissionType;
  classId: ClassId;
  reignEarned: number;
  xpEarned: number;
  completedAt: string;
}

// ─── NPC / World Data ─────────────────────────────────────────────────────────

export interface Npc {
  id: string;
  name: string;
  classId: ClassId;
  dialogue: string[];
  reward_bonus: number;
}

// ─── Dashboard / System Info ──────────────────────────────────────────────────

export interface SystemInfo {
  model: string;
  runtime: string;
  host: string;
  os: string;
  uptime: string;
  memory: string;
  lastHeartbeat: string;
  skills: string[];
  activeCrons: string[];
  github: string;
  claudeCodeAvailable: boolean;
}
