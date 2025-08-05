/**
 * RIROPO Core Parser - Adapted from https://github.com/vikcch/riropo
 * Original parser converted to TypeScript for Angular integration
 */

export interface RiropoParsedData {
  playersCount: number;
  buttonSeat: number;
  gameMode: number;
  mainInfo: any;
  players: any[];
  histories: any[];
  handsListItem: any;
  lines: string[];
  index: number;
}

export interface RiropoPlayer {
  name: string;
  seat: number;
  stack: number;
  cards?: string;
  isButton: boolean;
  isSmallBlind: boolean;
  isBigBlind: boolean;
  isHero: boolean;
  isAllIn: boolean;
  isWinner: boolean; // Adicionando propriedade isWinner para showdown
}

export interface RiropoAction {
  player: string;
  action: string;
  amount?: number;
  total_bet?: number; // Adicionando propriedade total_bet para raise
  street: string;
}

/**
 * Utility functions adapted from RIROPO
 */
export class RiropoUtils {
  /**
   * Get first element of array
   */
  static head<T>(array: T[]): T | undefined {
    return array[0];
  }

  /**
   * Get last element of array
   */
  static rear<T>(array: T[]): T | undefined {
    return array.slice(-1)[0];
  }

  /**
   * Remove money symbols and convert to number
   */
  static removeMoney(value: string): number {
    const clean = value.replace(/[€$£¥,\s]/g, '');
    return parseFloat(clean) || 0;
  }

  /**
   * Format number with thousand separators
   */
  static thousandSeparator(value: number | string): string {
    const arrSplit = `${value}`.replace('-', '').split('.');
    const wholePart = this.head(arrSplit) || '';
    const decimalPart = arrSplit.length > 1 ? `.${this.rear(arrSplit)}` : '';
    const sign = `${value}`.charAt(0) === '-' ? '-' : '';

    const r = [...wholePart].reduce((cur, acc, index, arr) => {
      const comma = (arr.length - index) % 3 === 0 ? ',' : '';
      return `${cur}${comma}${acc}`;
    }, '');

    return `${sign}${r}${decimalPart}`;
  }

  /**
   * Check if device is mobile
   */
  static isMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }

  /**
   * Check if in fullscreen mode
   */
  static isFullScreen(): boolean {
    return !!(document.fullscreenElement || 
             (document as any).webkitFullscreenElement || 
             (document as any).mozFullScreenElement || 
             (document as any).msFullscreenElement);
  }
}

/**
 * Business logic functions adapted from RIROPO
 */
export class RiropoBusiness {
  /**
   * Extract action amount from line
   */
  static actionAmount(line: string): number {
    const arrSplit = line.replace(/\sand\sis\sall-in$/gm, '').split(' ');
    const rearValue = RiropoUtils.removeMoney(this.rear(arrSplit) || '');
    return rearValue || 0;
  }

  /**
   * Extract collected amount from line
   */
  static collectedAmount(line: string): number {
    const arrSplit = line.split(' ');
    const dirtyValue = this.rear(arrSplit.filter(x => /^(?!pot).*\d$/gm.test(x)));
    return RiropoUtils.removeMoney(dirtyValue || '');
  }

  /**
   * Extract uncalled amount from line
   */
  static uncalledAmount(line: string): number {
    const dirtyValue = line.split(' ')[2];
    return RiropoUtils.removeMoney(dirtyValue || '');
  }

  /**
   * Check if line is uncalled bet
   */
  static isUncalledBet(value: string): boolean {
    return /^Uncalled\sbet\s\(.+\)\sreturned\sto\s/.test(value);
  }

  /**
   * Extract big blind from blinds string
   */
  static getBigBlind(value: string): number {
    if (!value) return 0;

    const targetPart = this.rear(value.split('/'));
    if (!targetPart) return 0;

    const rdc = (acc: { value: string; break: boolean }, cur: string) => {
      if (cur === '(' || cur === '[') acc.break = true;
      if (!acc.break) acc.value += cur;
      return acc;
    };

    const dirty = [...targetPart].reduce(rdc, { value: '', break: false });
    return RiropoUtils.removeMoney(dirty.value);
  }

  /**
   * Get last element of array
   */
  private static rear<T>(array: T[]): T | undefined {
    return array.slice(-1)[0];
  }
}

/**
 * Main RIROPO parser class
 */
export class RiropoCoreParser {
  /**
   * Count players in hand
   */
  static countPlayers(lines: string[]): number {
    const holeCardsLineCount = lines.indexOf('*** HOLE CARDS ***');
    const seats = (v: string, i: number) => v.startsWith('Seat ') && i < holeCardsLineCount;
    return lines.filter(seats).length;
  }

  /**
   * Get button seat from hand history
   */
  static getButtonSeat(lines: string[]): number {
    console.log('🔍 DEBUG: Buscando button seat...');
    console.log('🔍 DEBUG: Lines:', lines);
    
    // Buscar a linha que contém "is the button"
    const buttonLine = lines.find(line => line.includes('is the button'));
    console.log('🔍 DEBUG: Button line encontrada:', buttonLine);
    
    if (buttonLine) {
      const match = buttonLine.match(/Seat #(\d+) is the button/);
      console.log('🔍 DEBUG: Match do button:', match);
      return match ? Number(match[1]) : 1;
    }
    
    console.log('⚠️  DEBUG: Linha do button não encontrada, usando padrão 1');
    return 1;
  }

  /**
   * Get game mode from hand history
   * 1-> Tournament Hold'em  
   * 2-> Cash Hold'em  
   * 3-> Tournament PLO  
   * 4-> Cash PLO
   */
  static getGameMode(lines: string[]): number {
    const gameModeLine = lines[0];
    const tournament = gameModeLine.includes('Tournament');
    const Holdem = gameModeLine.includes('Hold');

    if (tournament) return Holdem ? 1 : 3;
    else return Holdem ? 2 : 4;
  }

  /**
   * Main parse function
   */
  static parse(lines: string[], index: number, count: number): RiropoParsedData {
    const gameMode = this.getGameMode(lines);
    const buttonSeat = this.getButtonSeat(lines);
    const mainInfo = this.createMainInfo(lines, index, count);
    const players = this.createPlayers(lines, buttonSeat, gameMode);
    const histories = this.createHistories(lines, players);
    const handsListItem = this.createHandsListItem(players, histories, mainInfo);

    return {
      playersCount: this.countPlayers(lines),
      buttonSeat,
      gameMode,
      mainInfo,
      players,
      histories,
      handsListItem,
      lines,
      index
    };
  }

  /**
   * Create main info object
   */
  private static createMainInfo(lines: string[], index: number, count: number): any {
    const handId = this.extractHandId(lines[0]);
    const tableName = this.extractTableName(lines[1]);
    const blinds = this.extractBlinds(lines[0]);

    return {
      handId,
      tableName,
      blinds,
      index,
      count
    };
  }

  /**
   * Create players array
   */
  private static createPlayers(lines: string[], buttonSeat: number, gameMode: number): RiropoPlayer[] {
    const players: RiropoPlayer[] = [];
    const holeCardsIndex = lines.indexOf('*** HOLE CARDS ***');

    // Extract seat information
    for (let i = 0; i < holeCardsIndex; i++) {
      const line = lines[i];
      if (line.startsWith('Seat ')) {
        const player = this.parsePlayerLine(line, buttonSeat);
        if (player) {
          players.push(player);
        }
      }
    }

    // Extract hero cards
    const heroCardsIndex = lines.findIndex(line => line.includes('Dealt to'));
    if (heroCardsIndex !== -1) {
      const heroLine = lines[heroCardsIndex];
      const heroName = this.extractHeroName(heroLine);
      const heroCards = this.extractHeroCards(heroLine);
      
      const heroPlayer = players.find(p => p.name === heroName);
      if (heroPlayer) {
        heroPlayer.isHero = true;
        heroPlayer.cards = heroCards;
      }
    }

    return players;
  }

  /**
   * Create histories array
   */
  private static createHistories(lines: string[], players: RiropoPlayer[]): RiropoAction[] {
    const histories: RiropoAction[] = [];
    let currentStreet = 'preflop';

    for (const line of lines) {
      // Detect street changes
      if (line.includes('*** FLOP ***')) {
        currentStreet = 'flop';
        console.log(`🔍 DEBUG: Street change to FLOP`);
        continue;
      } else if (line.includes('*** TURN ***')) {
        currentStreet = 'turn';
        console.log(`🔍 DEBUG: Street change to TURN`);
        continue;
      } else if (line.includes('*** RIVER ***')) {
        currentStreet = 'river';
        console.log(`🔍 DEBUG: Street change to RIVER`);
        continue;
      }

      // Log cartas do board
      if (line.includes('[') && line.includes(']') && !line.includes('Dealt to')) {
        console.log(`🔍 DEBUG: Board cards detected: "${line}"`);
      }

      // Parse actions
      const action = this.parseActionLine(line, currentStreet);
      if (action) {
        console.log(`🔍 DEBUG: Action parsed - ${action.player}: ${action.action} $${action.amount} (${action.street})`);
        histories.push(action);
      }
    }

    return histories;
  }

  /**
   * Extract hand ID from line
   */
  private static extractHandId(line: string): string {
    const match = line.match(/Hand #(\d+)/);
    return match ? match[1] : '';
  }

  /**
   * Extract table name from line
   */
  private static extractTableName(line: string): string {
    const match = line.match(/Table '([^']+)'/);
    return match ? match[1] : '';
  }

  /**
   * Extract blinds from line
   */
  private static extractBlinds(line: string): { small: number; big: number; ante?: number } {
    const blindsMatch = line.match(/\(([^)]+)\)/);
    if (!blindsMatch) return { small: 0, big: 0 };

    const blindsText = blindsMatch[1];
    const parts = blindsText.split('/');
    
    if (parts.length >= 2) {
      const small = this.removeMoney(parts[0]);
      const big = this.removeMoney(parts[1]);
      
      // Check for ante
      const anteMatch = blindsText.match(/\+(\d+)/);
      const ante = anteMatch ? this.removeMoney(anteMatch[1]) : undefined;

      return { small, big, ante };
    }

    return { small: 0, big: 0 };
  }

  /**
   * Remove money symbols and convert to number
   */
  private static removeMoney(value: string): number {
    const clean = value.replace(/[€$£¥,\s]/g, '');
    const result = parseFloat(clean) || 0;
    console.log(`🔍 DEBUG: removeMoney - "${value}" -> "${clean}" -> ${result}`);
    return result;
  }

  /**
   * Parse player line
   */
  private static parsePlayerLine(line: string, buttonSeat: number): RiropoPlayer | null {
    // Seat 1: PlayerName ($1000 in chips) [BTN] [SB] [BB]
    const match = line.match(/Seat (\d+): ([^(]+) \(([^)]+)\)/);
    if (!match) return null;

    const seat = Number(match[1]);
    const name = match[2].trim();
    const stackText = match[3];

    // Extract stack amount
    const stackMatch = stackText.match(/\$([\d,]+)/);
    const stack = stackMatch ? this.removeMoney(stackMatch[1]) : 0;

    // Extract position indicators from the full line
    const isButton = line.includes('[BTN]') || seat === buttonSeat;
    const isSmallBlind = line.includes('[SB]');
    const isBigBlind = line.includes('[BB]');

    console.log(`🔍 DEBUG: parsePlayerLine - ${name}:`);
    console.log(`  - Line: ${line}`);
    console.log(`  - isButton: ${isButton} (line includes [BTN]: ${line.includes('[BTN]')}, seat === buttonSeat: ${seat === buttonSeat})`);
    console.log(`  - isSmallBlind: ${isSmallBlind} (line includes [SB]: ${line.includes('[SB]')})`);
    console.log(`  - isBigBlind: ${isBigBlind} (line includes [BB]: ${line.includes('[BB]')})`);

    return {
      name,
      seat,
      stack,
      isButton,
      isSmallBlind,
      isBigBlind,
      isHero: false,
      isAllIn: false,
      isWinner: false // Inicialmente, nenhum jogador é vencedor
    };
  }

  /**
   * Extract hero name from dealt line
   */
  private static extractHeroName(line: string): string {
    const match = line.match(/Dealt to ([^[]+)/);
    return match ? match[1].trim() : '';
  }

  /**
   * Extract hero cards from dealt line
   */
  private static extractHeroCards(line: string): string {
    const match = line.match(/\[([^\]]+)\]/);
    return match ? match[1] : '';
  }

  /**
   * Parse action line
   */
  private static parseActionLine(line: string, street: string): RiropoAction | null {
    if (!line.trim() || line.includes('***')) return null;

    console.log(`🔍 DEBUG: parseActionLine - "${line}"`);

    if (line.includes('calls')) {
      const action = this.parseCallAction(line, street);
      console.log(`🔍 DEBUG: Call action parsed:`, action);
      return action;
    } else if (line.includes('raises')) {
      const action = this.parseRaiseAction(line, street);
      console.log(`🔍 DEBUG: Raise action parsed:`, action);
      return action;
    } else if (line.includes('folds')) {
      const action = this.parseFoldAction(line, street);
      console.log(`🔍 DEBUG: Fold action parsed:`, action);
      return action;
    } else if (line.includes('checks')) {
      const action = this.parseCheckAction(line, street);
      console.log(`🔍 DEBUG: Check action parsed:`, action);
      return action;
    } else if (line.includes('bets')) {
      const action = this.parseBetAction(line, street);
      console.log(`🔍 DEBUG: Bet action parsed:`, action);
      return action;
    } else if (line.includes('all-in')) {
      const action = this.parseAllInAction(line, street);
      console.log(`🔍 DEBUG: All-in action parsed:`, action);
      return action;
    }

    console.log(`⚠️  DEBUG: No action pattern matched for: "${line}"`);
    return null;
  }

  /**
   * Parse call action
   */
  private static parseCallAction(line: string, street: string): RiropoAction | null {
    // Padrão para "calls $X" - captura o valor após o $
    const match = line.match(/^([^:]+): calls \$([0-9,]+)/);
    if (!match) {
      console.log(`⚠️  DEBUG: parseCallAction - regex não funcionou para: "${line}"`);
      return null;
    }

    const player = match[1].trim();
    const callAmount = this.removeMoney(match[2]);

    console.log(`🔍 DEBUG: parseCallAction - ${player}: call=${callAmount}`);

    return {
      player,
      action: 'call',
      amount: callAmount,
      street
    };
  }

  /**
   * Parse raise action
   */
  private static parseRaiseAction(line: string, street: string): RiropoAction | null {
    // Padrão para "raises $X to $Y" - captura o valor do raise (X)
    const match = line.match(/^([^:]+): raises \$([0-9,]+) to \$([0-9,]+)/);
    if (!match) {
      console.log(`⚠️  DEBUG: parseRaiseAction - regex não funcionou para: "${line}"`);
      return null;
    }

    const player = match[1].trim();
    const raiseAmount = this.removeMoney(match[2]); // Valor do raise
    const totalAmount = this.removeMoney(match[3]); // Valor total

    console.log(`🔍 DEBUG: parseRaiseAction - ${player}: raise=${raiseAmount}, total=${totalAmount}`);

    return {
      player,
      action: 'raise',
      amount: raiseAmount, // Usar o valor do raise
      street
    };
  }

  /**
   * Parse fold action
   */
  private static parseFoldAction(line: string, street: string): RiropoAction | null {
    const match = line.match(/^([^:]+): folds/);
    if (!match) return null;

    return {
      player: match[1].trim(),
      action: 'fold',
      street
    };
  }

  /**
   * Parse check action
   */
  private static parseCheckAction(line: string, street: string): RiropoAction | null {
    const match = line.match(/^([^:]+): checks/);
    if (!match) return null;

    return {
      player: match[1].trim(),
      action: 'check',
      street
    };
  }

  /**
   * Parse bet action
   */
  private static parseBetAction(line: string, street: string): RiropoAction | null {
    // Padrão para "bets $X" - captura o valor após o $
    const match = line.match(/^([^:]+): bets \$([0-9,]+)/);
    if (!match) {
      console.log(`⚠️  DEBUG: parseBetAction - regex não funcionou para: "${line}"`);
      return null;
    }

    const player = match[1].trim();
    const betAmount = this.removeMoney(match[2]);

    console.log(`🔍 DEBUG: parseBetAction - ${player}: bet=${betAmount}`);

    return {
      player,
      action: 'bet',
      amount: betAmount,
      street
    };
  }

  /**
   * Parse all-in action
   */
  private static parseAllInAction(line: string, street: string): RiropoAction | null {
    const match = line.match(/^([^:]+): ([^$]+) and is all-in/);
    if (!match) return null;

    return {
      player: match[1].trim(),
      action: 'all-in',
      amount: this.removeMoney(match[2]),
      street
    };
  }

  /**
   * Create hands list item
   */
  private static createHandsListItem(players: RiropoPlayer[], histories: RiropoAction[], mainInfo: any): any {
    return {
      players,
      histories,
      mainInfo,
      timestamp: Date.now()
    };
  }
} 