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
  handId: string; // matches OpenFang hand
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
  risk?: number; // 0-1 for trader/oracle
  security_level?: number; // 1-5 for scout
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
  predictionsMade?: number;     // oracle only
  predictionsCorrect?: number;  // oracle only
  tradesWon?: number;           // trader only
  tradesLost?: number;          // trader only
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

// ─── Game State ────────────────────────────────────────────────────────────────

export interface GameState {
  sigbot: Sigbot | null;
  activeMission: ActiveMission | null;
  missionHistory: CompletedMission[];
  leaderboard: LeaderboardEntry[];
  gameStarted: boolean;
  view: 'home' | 'missions' | 'sigbot' | 'leaderboard';
}

export interface ActiveMission {
  mission: Mission;
  startedAt: string;
  endsAt: string;
  progress: number; // 0-100
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
  reward_bonus: number; // extra reign multiplier
}
