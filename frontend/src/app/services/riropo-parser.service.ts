import { Injectable } from '@angular/core';

export interface RiropoHand {
  id: string;
  site: string;
  gameType: string;
  stakes: string;
  tableName: string;
  maxSeats: number;
  buttonSeat: number;
  players: RiropoPlayer[];
  blinds: {
    small: number;
    big: number;
    ante?: number;
  };
  heroCards?: string[];
  streets: RiropoStreet[];
  summary: {
    totalPot: number;
    rake: number;
    board?: string[];
  };
}

export interface RiropoPlayer {
  seat: number;
  name: string;
  stack: number;
  isButton?: boolean;
  isSmallBlind?: boolean;
  isBigBlind?: boolean;
  isHero?: boolean;
  cards?: string[];
  position?: string;
}

export interface RiropoStreet {
  name: string;
  cards?: string[];
  actions: RiropoAction[];
}

export interface RiropoAction {
  player: string;
  action: string;
  amount?: number;
  totalBet?: number;
  isAllIn?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class RiropoParserService {

  constructor() { }

  /**
   * Parse PokerStars hand history text into structured data
   */
  parseHandHistory(handHistoryText: string): RiropoHand | null {
    if (!handHistoryText || handHistoryText.trim().length === 0) {
      return null;
    }

    try {
      const lines = handHistoryText.split('\n').map(line => line.trim()).filter(line => line.length > 0);
      
      // Parse header
      const header = this.parseHeader(lines[0]);
      if (!header) {
        throw new Error('Invalid hand history header');
      }

      // Parse table info
      const tableInfo = this.parseTableInfo(lines[1]);
      if (!tableInfo) {
        throw new Error('Invalid table information');
      }

      // Parse players
      const { players, playersEndIndex } = this.parsePlayers(lines);

      // Parse blinds
      const { blinds, blindsEndIndex } = this.parseBlinds(lines, playersEndIndex);

      // Parse streets and actions
      const streets = this.parseStreetsAndActions(lines, blindsEndIndex);

      // Parse summary
      const summary = this.parseSummary(lines);

      const hand: RiropoHand = {
        id: header.handId,
        site: 'PokerStars',
        gameType: header.gameType,
        stakes: header.stakes,
        tableName: tableInfo.tableName,
        maxSeats: tableInfo.maxSeats,
        buttonSeat: tableInfo.buttonSeat,
        players: players,
        blinds: blinds,
        streets: streets,
        summary: summary
      };

      // Set hero cards if found
      const heroCards = this.findHeroCards(lines);
      if (heroCards) {
        hand.heroCards = heroCards.cards;
        // Mark hero player
        const heroPlayer = players.find(p => p.name === heroCards.playerName);
        if (heroPlayer) {
          heroPlayer.isHero = true;
          heroPlayer.cards = heroCards.cards;
        }
      }

      return hand;

    } catch (error) {
      console.error('Error parsing hand history:', error);
      return null;
    }
  }

  private parseHeader(headerLine: string): { handId: string; gameType: string; stakes: string } | null {
    // PokerStars Hand #257045862415: Tournament #3910307458, $0.98+$0.12 USD Hold'em No Limit
    const headerRegex = /PokerStars Hand #(\d+):\s+(.+?)\s+(.+)/;
    const match = headerLine.match(headerRegex);
    
    if (!match) {
      return null;
    }

    return {
      handId: match[1],
      gameType: match[2],
      stakes: match[3]
    };
  }

  private parseTableInfo(tableLine: string): { tableName: string; maxSeats: number; buttonSeat: number } | null {
    // Table '3910307458 12' 9-max Seat #3 is the button
    const tableRegex = /Table '([^']+)'\s+(\d+)-max\s+Seat #(\d+) is the button/;
    const match = tableLine.match(tableRegex);
    
    if (!match) {
      return null;
    }

    return {
      tableName: match[1],
      maxSeats: parseInt(match[2]),
      buttonSeat: parseInt(match[3])
    };
  }

  private parsePlayers(lines: string[]): { players: RiropoPlayer[]; playersEndIndex: number } {
    const players: RiropoPlayer[] = [];
    let index = 2; // Start after header and table info

    // Seat 1: jojosetubal (7835 in chips)
    const seatRegex = /Seat (\d+):\s+([^(]+)\s+\((\d+) in chips\)/;

    while (index < lines.length) {
      const line = lines[index];
      const match = line.match(seatRegex);
      
      if (!match) {
        break;
      }

      players.push({
        seat: parseInt(match[1]),
        name: match[2].trim(),
        stack: parseInt(match[3])
      });

      index++;
    }

    return { players, playersEndIndex: index };
  }

  private parseBlinds(lines: string[], startIndex: number): { blinds: any; blindsEndIndex: number } {
    const blinds: any = { small: 0, big: 0 };
    let index = startIndex;

    // Skip ante lines and find blinds
    while (index < lines.length) {
      const line = lines[index];
      
      // jojosetubal: posts ante 10
      if (line.includes('posts ante')) {
        const anteMatch = line.match(/posts ante (\d+)/);
        if (anteMatch && !blinds.ante) {
          blinds.ante = parseInt(anteMatch[1]);
        }
      }
      // Maks19111979: posts small blind 40
      else if (line.includes('posts small blind')) {
        const sbMatch = line.match(/posts small blind (\d+)/);
        if (sbMatch) {
          blinds.small = parseInt(sbMatch[1]);
        }
      }
      // SuKKinho: posts big blind 80
      else if (line.includes('posts big blind')) {
        const bbMatch = line.match(/posts big blind (\d+)/);
        if (bbMatch) {
          blinds.big = parseInt(bbMatch[1]);
        }
      }
      // *** HOLE CARDS *** indicates end of blinds section
      else if (line.includes('*** HOLE CARDS ***')) {
        break;
      }

      index++;
    }

    return { blinds, blindsEndIndex: index };
  }

  private parseStreetsAndActions(lines: string[], startIndex: number): RiropoStreet[] {
    const streets: RiropoStreet[] = [];
    let currentStreet: RiropoStreet | null = null;
    let index = startIndex;

    while (index < lines.length) {
      const line = lines[index];

      // Street headers
      if (line.includes('*** HOLE CARDS ***')) {
        currentStreet = { name: 'preflop', actions: [] };
        streets.push(currentStreet);
      }
      else if (line.includes('*** FLOP ***')) {
        const cards = this.extractBoardCards(line);
        currentStreet = { name: 'flop', cards, actions: [] };
        streets.push(currentStreet);
      }
      else if (line.includes('*** TURN ***')) {
        const cards = this.extractBoardCards(line);
        currentStreet = { name: 'turn', cards, actions: [] };
        streets.push(currentStreet);
      }
      else if (line.includes('*** RIVER ***')) {
        const cards = this.extractBoardCards(line);
        currentStreet = { name: 'river', cards, actions: [] };
        streets.push(currentStreet);
      }
      else if (line.includes('*** SUMMARY ***')) {
        break;
      }
      // Parse actions
      else if (currentStreet) {
        const action = this.parseAction(line);
        if (action) {
          currentStreet.actions.push(action);
        }
      }

      index++;
    }

    return streets;
  }

  private extractBoardCards(line: string): string[] {
    // *** FLOP *** [9d Qc 5h]
    const cardMatch = line.match(/\[([^\]]+)\]/);
    if (cardMatch) {
      return cardMatch[1].split(' ').filter(card => card.trim().length > 0);
    }
    return [];
  }

  private parseAction(line: string): RiropoAction | null {
    // petretudor: raises 546 to 626 and is all-in
    // phpro: folds
    // SuKKinho: checks

    const playerMatch = line.match(/^([^:]+):\s+(.+)$/);
    if (!playerMatch) {
      return null;
    }

    const playerName = playerMatch[1].trim();
    const actionText = playerMatch[2].trim();

    // Parse different action types
    if (actionText === 'folds') {
      return { player: playerName, action: 'fold' };
    }
    else if (actionText === 'checks') {
      return { player: playerName, action: 'check' };
    }
    else if (actionText.startsWith('calls')) {
      const callMatch = actionText.match(/calls (\d+)/);
      const amount = callMatch ? parseInt(callMatch[1]) : 0;
      return { player: playerName, action: 'call', amount };
    }
    else if (actionText.startsWith('bets')) {
      const betMatch = actionText.match(/bets (\d+)/);
      const amount = betMatch ? parseInt(betMatch[1]) : 0;
      return { player: playerName, action: 'bet', amount };
    }
    else if (actionText.startsWith('raises')) {
      const raiseMatch = actionText.match(/raises (\d+) to (\d+)/);
      if (raiseMatch) {
        const amount = parseInt(raiseMatch[1]);
        const totalBet = parseInt(raiseMatch[2]);
        const isAllIn = actionText.includes('all-in');
        return { player: playerName, action: 'raise', amount, totalBet, isAllIn };
      }
    }

    return null;
  }

  private findHeroCards(lines: string[]): { playerName: string; cards: string[] } | null {
    // Dealt to phpro [9d Qc]
    for (const line of lines) {
      const heroMatch = line.match(/Dealt to ([^[]+) \[([^\]]+)\]/);
      if (heroMatch) {
        const playerName = heroMatch[1].trim();
        const cards = heroMatch[2].split(' ').filter(card => card.trim().length > 0);
        return { playerName, cards };
      }
    }
    return null;
  }

  private parseSummary(lines: string[]): { totalPot: number; rake: number; board?: string[] } {
    const summary: { totalPot: number; rake: number; board?: string[] } = { totalPot: 0, rake: 0 };

    for (const line of lines) {
      // Total pot 290 | Rake 0
      const potMatch = line.match(/Total pot (\d+).*Rake (\d+)/);
      if (potMatch) {
        summary.totalPot = parseInt(potMatch[1]);
        summary.rake = parseInt(potMatch[2]);
      }

      // Board [9d Qc 5h 7s 2c]
      const boardMatch = line.match(/Board \[([^\]]+)\]/);
      if (boardMatch) {
        summary.board = boardMatch[1].split(' ').filter(card => card.trim().length > 0);
      }
    }

    return summary;
  }

  /**
   * Convert parsed hand to our internal format
   */
  convertToHandReplay(riropoHand: RiropoHand): any {
    // Convert RIROPO format to our HandReplay format
    return {
      hand_id: riropoHand.id,
      table_name: riropoHand.tableName,
      level: riropoHand.stakes,
      blinds: riropoHand.blinds,
      players: riropoHand.players.map(p => ({
        name: p.name,
        position: p.seat,
        stack: p.stack,
        is_button: p.isButton || false,
        is_small_blind: p.isSmallBlind || false,
        is_big_blind: p.isBigBlind || false,
        is_hero: p.isHero || false,
        cards: p.cards
      })),
      hero_cards: riropoHand.heroCards,
      streets: riropoHand.streets.map(s => ({
        name: s.name,
        cards: s.cards || [],
        actions: s.actions.map(a => ({
          player: a.player,
          action: a.action,
          amount: a.amount || 0,
          total_bet: a.totalBet || a.amount || 0
        }))
      }))
    };
  }
}

