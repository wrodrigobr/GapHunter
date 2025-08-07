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
  streets: RiropoStreet[];
  summary: RiropoSummary;
  blinds: { small: number; big: number; ante?: number };
  heroCards?: string[];
}

export interface RiropoPlayer {
  seat: number;
  name: string;
  stack: number;
  isButton: boolean;
  isSmallBlind: boolean;
  isBigBlind: boolean;
  isHero: boolean;
  cards?: string[];
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

export interface RiropoSummary {
  totalPot: number;
  rake: number;
  board?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class RiropoOriginalParserService {

  constructor() { }

  /**
   * Parse hand history using original RIROPO logic
   */
  parseHandHistory(handHistoryText: string): RiropoHand | null {
    if (!handHistoryText || handHistoryText.trim().length === 0) {
      return null;
    }

    try {
      const lines = handHistoryText.split('\n').map(line => line.trim()).filter(line => line.length > 0);
      
      // Parse using original RIROPO functions
      const playerCount = this.countPlayers(lines);
      const buttonSeat = this.getButtonSeat(lines);
      const gameMode = this.getGameMode(lines);
      
      // Parse header
      const header = this.parseHeader(lines);
      if (!header) {
        throw new Error('Invalid hand history header');
      }

      // Parse table info
      const tableInfo = this.parseTableInfo(lines);
      if (!tableInfo) {
        throw new Error('Invalid table information');
      }

      // Parse players
      const { players, playersEndIndex } = this.parsePlayers(lines);

      // Parse blinds
      const blinds = this.parseBlinds(lines, playersEndIndex);

      // Parse streets and actions
      const streets = this.parseStreetsAndActions(lines, playersEndIndex);

      // Parse summary
      const summary = this.parseSummary(lines);

      const hand: RiropoHand = {
        id: header.handId,
        site: 'PokerStars',
        gameType: header.gameType,
        stakes: header.stakes,
        tableName: tableInfo.tableName,
        maxSeats: tableInfo.maxSeats,
        buttonSeat: buttonSeat,
        players: players,
        streets: streets,
        summary: summary,
        blinds: blinds
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

  /**
   * Count players - original RIROPO logic
   */
  private countPlayers(lines: string[]): number {
    const holeCardsLineCount = lines.indexOf('*** HOLE CARDS ***');
    const seats = (v: string, i: number) => v.startsWith('Seat ') && i < holeCardsLineCount;
    return lines.filter(seats).length;
  }

  /**
   * Get button seat - original RIROPO logic
   */
  private getButtonSeat(lines: string[]): number {
    // Procura por "Seat #X is the button" em qualquer linha
    for (const line of lines) {
      const match = line.match(/Seat #(\d+) is the button/);
      if (match) {
        return Number(match[1]);
      }
    }
    
    // Se não encontrar, procura na linha da mesa
    const buttonLine = lines[1];
    const match = buttonLine.match(/#(\d+)/);
    return match ? Number(match[1]) : 1;
  }

  /**
   * Get game mode - original RIROPO logic
   * 1-> Tournament Hold'em  
   * 2-> Cash Hold'em  
   * 3-> Tournament PLO  
   * 4-> Cash PLO
   */
  private getGameMode(lines: string[]): number {
    const gameModeLine = lines[0];
    const tournament = gameModeLine.includes('Tournament');
    const holdem = gameModeLine.includes('Hold');
    
    if (tournament) return holdem ? 1 : 3;
    else return holdem ? 2 : 4;
  }

  private parseHeader(lines: string[]) {
    // PokerStars Hand #257045862415: Tournament #3910307458, $0.98+$0.12 USD Hold'em No Limit
    for (const line of lines) {
      const headerRegex = /PokerStars Hand #(\d+):\s+(.+)/;
      const match = line.match(headerRegex);
      
      if (match) {
        return {
          handId: match[1],
          gameType: match[2],
          stakes: match[2].includes('Tournament') ? 'Tournament' : 'Cash'
        };
      }
    }
    return null;
  }

  private parseTableInfo(lines: string[]) {
    // Table 'Akiyama II' 6-max Seat #5 is the button
    // ou Table '3910307458 12' VI
    for (const line of lines) {
      // Primeiro tenta o formato padrão
      let tableRegex = /Table '([^']+)'\s+(\d+)-max\s+Seat #(\d+) is the button/;
      let match = line.match(tableRegex);
      
      if (match) {
        return {
          tableName: match[1],
          maxSeats: parseInt(match[2]),
          buttonSeat: parseInt(match[3])
        };
      }

      // Tenta formato alternativo (torneios)
      tableRegex = /Table '([^']+)'\s+(\w+)/;
      match = line.match(tableRegex);
      
      if (match) {
        // Para torneios, assume 9-max por padrão
        return {
          tableName: match[1],
          maxSeats: 9,
          buttonSeat: 1 // Será corrigido pelo getButtonSeat
        };
      }
    }
    return null;
  }

  private parseBlinds(lines: string[], startIndex: number) {
    const blinds: { small: number; big: number; ante?: number } = { small: 0, big: 0 };

    for (let i = startIndex; i < lines.length; i++) {
      const line = lines[i];
      
      // posts the ante
      if (line.includes('posts the ante')) {
        const anteMatch = line.match(/posts the ante (\d+)/);
        if (anteMatch && !blinds.ante) {
          blinds.ante = parseInt(anteMatch[1]);
        }
      }
      // posts small blind
      else if (line.includes('posts small blind')) {
        const sbMatch = line.match(/posts small blind (\d+)/);
        if (sbMatch) {
          blinds.small = parseInt(sbMatch[1]);
        }
      }
      // posts big blind
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
    }

    return blinds;
  }

  private parsePlayers(lines: string[]) {
    const players: RiropoPlayer[] = [];
    let playersEndIndex = 0;

    console.log('🔍 DEBUG: Iniciando parsePlayers...');
    console.log('🔍 DEBUG: Total de linhas:', lines.length);

    // Seat 1: jojosetubal (7835 in chips)
    // Seat 5: SuKKinho ($3918 in chips) [BTN]
    // Seat 6: martelli1990 ($3000 in chips) [SB]
    const seatRegex = /Seat (\d+):\s+([^($]+)\s+\([\$]?(\d+) in chips\)/;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      console.log(`🔍 DEBUG: Linha ${i}: "${line}"`);
      
      const match = line.match(seatRegex);
      
      if (match) {
        console.log('🔍 DEBUG: Match encontrado:', match);
        const player = {
          seat: parseInt(match[1]),
          name: match[2].trim(),
          stack: parseInt(match[3]),
          isButton: false,
          isSmallBlind: false,
          isBigBlind: false,
          isHero: false
        };
        
        // Check for position indicators in the line
        if (line.includes('[BTN]')) player.isButton = true;
        if (line.includes('[SB]')) player.isSmallBlind = true;
        if (line.includes('[BB]')) player.isBigBlind = true;
        
        players.push(player);
        playersEndIndex = i + 1;
        console.log('🔍 DEBUG: Jogador adicionado:', player);
      } else if (line.includes('*** HOLE CARDS ***')) {
        console.log('🔍 DEBUG: Encontrou HOLE CARDS, parando parsing de jogadores');
        break;
      }
    }

    console.log('🔍 DEBUG: Total de jogadores encontrados:', players.length);
    console.log('🔍 DEBUG: Jogadores:', players);
    return { players, playersEndIndex };
  }

  private parseStreetsAndActions(lines: string[], startIndex: number) {
    const streets: RiropoStreet[] = [];
    let currentStreet: RiropoStreet | null = null;

    for (let i = startIndex; i < lines.length; i++) {
      const line = lines[i];

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
        // For turn, only get the new card (4th card)
        const turnCard = cards.length > 3 ? [cards[3]] : [];
        currentStreet = { name: 'turn', cards: turnCard, actions: [] };
        streets.push(currentStreet);
      }
      else if (line.includes('*** RIVER ***')) {
        const cards = this.extractBoardCards(line);
        // For river, only get the new card (5th card)
        const riverCard = cards.length > 4 ? [cards[4]] : [];
        currentStreet = { name: 'river', cards: riverCard, actions: [] };
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
    else if (actionText.startsWith('posts small blind')) {
      const sbMatch = actionText.match(/posts small blind (\d+)/);
      const amount = sbMatch ? parseInt(sbMatch[1]) : 0;
      return { player: playerName, action: 'small_blind', amount };
    }
    else if (actionText.startsWith('posts big blind')) {
      const bbMatch = actionText.match(/posts big blind (\d+)/);
      const amount = bbMatch ? parseInt(bbMatch[1]) : 0;
      return { player: playerName, action: 'big_blind', amount };
    }
    else if (actionText.startsWith('posts the ante')) {
      const anteMatch = actionText.match(/posts the ante (\d+)/);
      const amount = anteMatch ? parseInt(anteMatch[1]) : 0;
      return { player: playerName, action: 'ante', amount };
    }

    return null;
  }

  private findHeroCards(lines: string[]) {
    // Dealt to phpro [9d Qc]
    for (const line of lines) {
      const heroMatch = line.match(/Dealt to ([^[]+) \[([^\]]+)\]/);
      if (heroMatch) {
        const playerName = heroMatch[1].trim();
        const cardsStr = heroMatch[2];
        const cards = cardsStr.split(' ').filter(card => card.trim().length > 0);
        return { playerName, cards };
      }
    }
    return null;
  }

  private parseSummary(lines: string[]): RiropoSummary {
    const summary: RiropoSummary = { totalPot: 0, rake: 0 };

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
}

