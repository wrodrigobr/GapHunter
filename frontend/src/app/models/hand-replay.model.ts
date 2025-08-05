export interface PlayerInfo {
  name: string;
  position: number;
  stack: number;
  cards?: string;
  is_hero: boolean;
  is_button: boolean;
  is_small_blind: boolean;
  is_big_blind: boolean;
  current_bet?: number;
  is_active?: boolean;
  is_folded?: boolean;
}

export interface PlayerAction {
  player: string;
  action: string;
  amount: number;
  total_bet: number;
  timestamp: number;
  street?: string;  // Opcional para compatibilidade com dados do banco
}

export interface GameStreet {
  name: string;
  cards: string[];
  actions: PlayerAction[];
}

export interface HandReplay {
  hand_id: string;
  tournament_id: string;
  table_name: string;
  level: string;
  blinds: {
    small: number;
    big: number;
    ante: number;
  };
  players: PlayerInfo[];
  streets: GameStreet[];
  hero_name: string;
  hero_cards: string[];
  local_analysis?: string;
} 