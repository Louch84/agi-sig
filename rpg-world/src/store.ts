import type { GameState, Sigbot, CompletedMission, ChatMessage } from './types';
import { LEADERBOARD, getLevelFromXP } from './data';

const STORAGE_KEY = 'agi_realm_state';

const INITIAL_STATE: GameState = {
  sigbot: null,
  activeMission: null,
  missionHistory: [],
  leaderboard: LEADERBOARD,
  gameStarted: false,
  view: 'home',
  chatMessages: [],
  pendingBotReply: false
};

export function loadState(): GameState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...INITIAL_STATE };
    const parsed = JSON.parse(raw) as GameState;
    parsed.leaderboard = LEADERBOARD;
    // Ensure new fields exist
    if (!parsed.chatMessages) parsed.chatMessages = [];
    if (parsed.pendingBotReply === undefined) parsed.pendingBotReply = false;
    return parsed;
  } catch {
    return { ...INITIAL_STATE };
  }
}

export function addChatMessage(state: GameState, role: 'lou' | 'sigbotti', text: string): GameState {
  const msg: ChatMessage = {
    id: `msg_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
    role,
    text,
    timestamp: new Date().toISOString()
  };
  return { ...state, chatMessages: [...state.chatMessages, msg] };
}

export function setPendingReply(state: GameState, pending: boolean): GameState {
  return { ...state, pendingBotReply: pending };
}

export function saveState(state: GameState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.error('Failed to save game state', e);
  }
}

export function createSigbot(name: string, classId: Sigbot['classId']): Sigbot {
  return {
    id: `sigbot_${Date.now()}`,
    name,
    classId,
    level: 1,
    xp: 0,
    reign: 0,
    reputation: 0,
    missionsCompleted: 0,
    predictionsMade: 0,
    predictionsCorrect: 0,
    tradesWon: 0,
    tradesLost: 0,
    createdAt: new Date().toISOString()
  };
}

export function completeMission(
  state: GameState,
  reignEarned: number,
  xpEarned: number,
  isWin?: boolean
): GameState {
  if (!state.sigbot) return state;

  const newXp = state.sigbot.xp + xpEarned;
  const newLevel = getLevelFromXP(newXp);
  const updatedSigbot = { ...state.sigbot, xp: newXp, level: newLevel };

  if (state.sigbot.classId === 'oracle' && isWin !== undefined) {
    updatedSigbot.predictionsMade = (state.sigbot.predictionsMade || 0) + 1;
    if (isWin) updatedSigbot.predictionsCorrect = (state.sigbot.predictionsCorrect || 0) + 1;
  }
  if (state.sigbot.classId === 'trader' && isWin !== undefined) {
    if (isWin) updatedSigbot.tradesWon = (state.sigbot.tradesWon || 0) + 1;
    else updatedSigbot.tradesLost = (state.sigbot.tradesLost || 0) + 1;
  }

  updatedSigbot.reign += reignEarned;
  updatedSigbot.reputation += Math.floor(xpEarned / 10);
  updatedSigbot.missionsCompleted += 1;

  const completedMission: CompletedMission = {
    missionName: state.activeMission?.mission.name || 'Unknown',
    missionType: state.activeMission?.mission.type || 'data_heist',
    classId: state.sigbot.classId,
    reignEarned,
    xpEarned,
    completedAt: new Date().toISOString()
  };

  const newHistory = [completedMission, ...state.missionHistory].slice(0, 50);
  const newLeaderboard = updateLeaderboard(state, updatedSigbot);

  return {
    ...state,
    sigbot: updatedSigbot,
    activeMission: null,
    missionHistory: newHistory,
    leaderboard: newLeaderboard
  };
}

function updateLeaderboard(state: GameState, sigbot: Sigbot): typeof state.leaderboard {
  const entry = {
    rank: 0,
    name: sigbot.name,
    classId: sigbot.classId,
    reign: sigbot.reign,
    reputation: sigbot.reputation,
    level: sigbot.level
  };

  const existing = state.leaderboard.findIndex(e => e.name === sigbot.name);
  let updated: typeof state.leaderboard;

  if (existing >= 0) {
    updated = [...state.leaderboard];
    updated[existing] = { ...updated[existing], ...entry };
  } else {
    updated = [...state.leaderboard, entry];
  }

  updated.sort((a, b) => b.reign - a.reign);
  updated = updated.slice(0, 100);
  updated.forEach((e, i) => { e.rank = i + 1; });

  return updated;
}

export function formatReign(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n.toString();
}
