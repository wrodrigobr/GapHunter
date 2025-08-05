import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { RiropoCoreParser, RiropoParsedData } from './riropo-core-parser';

export interface RiropoPlayer {
  name: string;
  seat: number;
  stack: number;
  cards?: string;
  isButton: boolean;
  isSmallBlind: boolean;
  isBigBlind: boolean;
  isHero: boolean;
  isActive: boolean;
  isFolded: boolean;
  currentBet: number;
  bet: number; // Adicionando propriedade bet para compatibilidade com template
  isAllIn: boolean;
  isChecked: boolean; // Adicionando propriedade isChecked
  isWinner: boolean; // Adicionando propriedade isWinner para showdown
  position: string;
}

export interface RiropoAction {
  player: string;
  action: string;
  amount?: number;
  total_bet?: number; // Adicionando propriedade total_bet para raise
  street: string;
  timestamp: number;
  cards?: string; // Adicionando propriedade cards para ações de showdown
}

export interface RiropoHand {
  handId: string;
  tableName: string;
  tournamentId?: string;
  gameMode: 'cash' | 'tournament';
  gameType: 'holdem' | 'omaha';
  blinds: {
    small: number;
    big: number;
    ante?: number;
  };
  buttonSeat: number;
  players: RiropoPlayer[];
  actions: RiropoAction[];
  board: string[];
  streets?: any[]; // Adicionando propriedade streets para compatibilidade
  pot: number;
  hero: string;
  heroCards: string;
  winner?: string;
  rawText: string;
}



@Injectable({
  providedIn: 'root'
})
export class RiropoParserService {
  private currentHandSubject = new BehaviorSubject<RiropoHand | null>(null);
  public currentHand$ = this.currentHandSubject.asObservable();
  private rawText: string = '';

  constructor() {}

  /**
   * Parse hand history text using RIROPO parser
   */
  parseHandHistory(handText: string): RiropoHand | null {
    try {
      // Store raw text for SUMMARY parsing
      this.rawText = handText;
      
      // Split the hand text into lines
      const lines = handText.trim().split('\n');
      
      // Use the RIROPO parser (we'll import it)
      const parsedData = this.parseWithRiropo(lines, 0, 1);
      
      if (!parsedData) {
        console.error('Failed to parse hand history');
        return null;
      }

      // Convert RIROPO format to our format
      const hand = this.convertRiropoToHand(parsedData, handText);
      
      this.currentHandSubject.next(hand);
      return hand;
    } catch (error) {
      console.error('Error parsing hand history:', error);
      return null;
    }
  }

  /**
   * Parse using RIROPO parser
   */
  private parseWithRiropo(lines: string[], index: number, count: number): RiropoParsedData | null {
    try {
      return RiropoCoreParser.parse(lines, index, count);
    } catch (error) {
      console.error('Error in RIROPO parser:', error);
      return null;
    }
  }

  /**
   * Convert RIROPO format to our hand format
   */
  private convertRiropoToHand(parsedData: RiropoParsedData, rawText: string): RiropoHand {
    console.log('🔍 DEBUG: Convertendo dados para formato RIROPO...');
    console.log('📊 DEBUG: Dados parseados:', parsedData);
    
    // Extract basic info
    const handId = this.extractHandId(parsedData.lines[0]);
    const tableName = this.extractTableName(parsedData.lines[1]);
    const blinds = this.extractBlinds(parsedData.lines[0]);
    const gameMode = parsedData.gameMode === 1 || parsedData.gameMode === 3 ? 'tournament' : 'cash';
    const gameType = parsedData.gameMode === 1 || parsedData.gameMode === 2 ? 'holdem' : 'omaha';

    console.log('🔍 DEBUG: Button seat do parsedData:', parsedData.buttonSeat);
    console.log('🔍 DEBUG: Players do parsedData:', parsedData.players);

    // Convert players
    const players: RiropoPlayer[] = parsedData.players.map((player: any, index: number) => {
      const isButton = player.seat === parsedData.buttonSeat || player.is_button || false;
      const isSmallBlind = player.isSmallBlind || player.is_small_blind || false;
      const isBigBlind = player.isBigBlind || player.is_big_blind || false;
      const isHero = player.isHero || player.is_hero || false;
      
      console.log(`🔍 DEBUG: Player ${index + 1} - ${player.name}:`);
      console.log(`  - Seat: ${player.seat}`);
      console.log(`  - Button seat: ${parsedData.buttonSeat}`);
      console.log(`  - is_button (raw): ${player.is_button}`);
      console.log(`  - is_small_blind (raw): ${player.is_small_blind}`);
      console.log(`  - is_big_blind (raw): ${player.is_big_blind}`);
      console.log(`  - is_hero (raw): ${player.is_hero}`);
      console.log(`  - Calculated isButton: ${isButton}`);
      console.log(`  - Calculated isSmallBlind: ${isSmallBlind}`);
      console.log(`  - Calculated isBigBlind: ${isBigBlind}`);
      
      // Log adicional para verificar se os campos estão sendo definidos
      if (isSmallBlind) {
        console.log(`🎯 DEBUG: ${player.name} é SMALL BLIND`);
      }
      if (isBigBlind) {
        console.log(`🎯 DEBUG: ${player.name} é BIG BLIND`);
      }
      
      return {
        name: player.name,
        seat: player.seat,
        stack: player.stack,
        cards: player.cards,
        isButton: isButton,
        isSmallBlind: isSmallBlind,
        isBigBlind: isBigBlind,
        isHero: isHero,
        isActive: false,
        isFolded: false,
        currentBet: 0,
        bet: 0, // Inicializar bet como 0
        isAllIn: false, // Inicializar isAllIn como false
        isChecked: false, // Inicializar isChecked como false
        isWinner: false, // Inicializar isWinner como false
        position: this.getPositionName(player.seat, parsedData.buttonSeat, parsedData.players.length)
      };
    });

    console.log('🔍 DEBUG: Players convertidos:', players);
    console.log('🔍 DEBUG: Raw text (primeiros 500 chars):', rawText.substring(0, 500));

    // Extract board cards
    const board = this.extractBoard(parsedData.lines);

    // Extract actions
    const actions: RiropoAction[] = this.extractActions(parsedData.histories);

    // Find hero
    const hero = players.find(p => p.isHero)?.name || '';

    // Calculate pot
    const pot = this.calculatePot(actions, blinds);

    return {
      handId,
      tableName,
      gameMode,
      gameType,
      blinds,
      buttonSeat: parsedData.buttonSeat,
      players,
      actions,
      board,
      pot,
      hero,
      heroCards: players.find(p => p.isHero)?.cards || '',
      rawText
    };
  }

  /**
   * Extract hand ID from the first line
   */
  private extractHandId(line: string): string {
    const match = line.match(/Hand #(\d+)/);
    return match ? match[1] : '';
  }

  /**
   * Extract table name from the second line
   */
  private extractTableName(line: string): string {
    const match = line.match(/Table '([^']+)'/);
    return match ? match[1] : '';
  }

  /**
   * Extract blinds from the first line
   */
  private extractBlinds(line: string): { small: number; big: number; ante?: number } {
    const blindsMatch = line.match(/\(([^)]+)\)/);
    if (!blindsMatch) return { small: 0, big: 0 };

    const blindsText = blindsMatch[1];
    const parts = blindsText.split('/');
    
    if (parts.length >= 2) {
      const small = this.parseAmount(parts[0]);
      const big = this.parseAmount(parts[1]);
      
      // Check for ante
      const anteMatch = blindsText.match(/\+(\d+)/);
      const ante = anteMatch ? this.parseAmount(anteMatch[1]) : undefined;

      return { small, big, ante };
    }

    return { small: 0, big: 0 };
  }

  /**
   * Parse amount string to number
   */
  private parseAmount(amountStr: string): number {
    // Remove currency symbols and convert to number
    const clean = amountStr.replace(/[€$£¥,]/g, '');
    return parseFloat(clean) || 0;
  }

  /**
   * Extract board cards from hand history
   */
  private extractBoard(lines: string[]): string[] {
    const board: string[] = [];
    console.log('🔍 DEBUG: extractBoard - linhas recebidas:', lines.length);
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      console.log('🔍 DEBUG: extractBoard - processando linha:', line);
      
      if (line.includes('*** FLOP ***')) {
        console.log('🔍 DEBUG: extractBoard - encontrou FLOP');
        // Procurar cartas na linha atual ou na próxima
        let cardsLine = line;
        if (!line.includes('[') && i + 1 < lines.length) {
          cardsLine = lines[i + 1];
          console.log('🔍 DEBUG: extractBoard - procurando cartas na próxima linha:', cardsLine);
        }
        
        const match = cardsLine.match(/\[([^\]]+)\]/);
        if (match) {
          console.log('🔍 DEBUG: extractBoard - match FLOP:', match[1]);
          board.push(...match[1].split(' '));
        } else {
          console.log('⚠️  DEBUG: extractBoard - não encontrou match para FLOP');
        }
      } else if (line.includes('*** TURN ***')) {
        console.log('🔍 DEBUG: extractBoard - encontrou TURN');
        // Procurar cartas na linha atual ou na próxima
        let cardsLine = line;
        if (!line.includes('[') && i + 1 < lines.length) {
          cardsLine = lines[i + 1];
          console.log('🔍 DEBUG: extractBoard - procurando cartas na próxima linha:', cardsLine);
        }
        
        // Encontrar o segundo par de colchetes (carta do turn)
        const matches = cardsLine.match(/\[([^\]]+)\]/g);
        if (matches && matches.length >= 2) {
          const turnCard = matches[1].replace(/[\[\]]/g, '');
          console.log('🔍 DEBUG: extractBoard - match TURN:', turnCard);
          board.push(turnCard);
        } else {
          console.log('⚠️  DEBUG: extractBoard - não encontrou match para TURN');
        }
      } else if (line.includes('*** RIVER ***')) {
        console.log('🔍 DEBUG: extractBoard - encontrou RIVER');
        // Procurar cartas na linha atual ou na próxima
        let cardsLine = line;
        if (!line.includes('[') && i + 1 < lines.length) {
          cardsLine = lines[i + 1];
          console.log('🔍 DEBUG: extractBoard - procurando cartas na próxima linha:', cardsLine);
        }
        
        // Encontrar o segundo par de colchetes (carta do river)
        const matches = cardsLine.match(/\[([^\]]+)\]/g);
        if (matches && matches.length >= 2) {
          const riverCard = matches[1].replace(/[\[\]]/g, '');
          console.log('🔍 DEBUG: extractBoard - match RIVER:', riverCard);
          board.push(riverCard);
        } else {
          console.log('⚠️  DEBUG: extractBoard - não encontrou match para RIVER');
        }
      }
    }

    console.log('🔍 DEBUG: extractBoard - board final:', board);
    return board;
  }

  /**
   * Extract actions from histories
   */
  private extractActions(histories: any[]): RiropoAction[] {
    const actions: RiropoAction[] = [];
    let timestamp = 0;

    for (const history of histories) {
      if (history.action && history.player) {
        actions.push({
          player: history.player,
          action: history.action,
          amount: history.amount,
          street: history.street || 'preflop',
          timestamp: timestamp++
        });
      }
    }

    // Adicionar ações do SUMMARY se existirem
    this.addSummaryActions(actions, timestamp);

    return actions;
  }

  /**
   * Add actions from SUMMARY section
   */
  private addSummaryActions(actions: RiropoAction[], startTimestamp: number): void {
    // Procurar por linhas do SUMMARY no rawText
    const summaryLines = this.extractSummaryLines();
    
    for (const line of summaryLines) {
      // Extrair informações de quem ganhou o pote
      const collectedMatch = line.match(/collected \$([\d,]+)/i);
      const wonMatch = line.match(/won \$([\d,]+)/i);
      const showedMatch = line.match(/showed (.+) and won/i);
      const showedLostMatch = line.match(/showed (.+) and lost/i);
      const showedWonMatch = line.match(/showed and won/i);
      
      if (collectedMatch || wonMatch || showedMatch || showedLostMatch || showedWonMatch) {
        const playerMatch = line.match(/Seat \d+: ([^(]+)/);
        if (playerMatch) {
          const player = playerMatch[1].trim();
          const amount = this.parseAmount(collectedMatch?.[1] || wonMatch?.[1] || '0');
          
          // Extrair cartas se disponível
          let cards = '';
          if (showedMatch) {
            const cardsMatch = line.match(/showed \[([^\]]+)\]/);
            if (cardsMatch) {
              cards = cardsMatch[1];
              console.log(`🔍 DEBUG: Cartas do vencedor ${player}: ${cards}`);
            }
          } else if (showedLostMatch) {
            const cardsMatch = line.match(/showed \[([^\]]+)\]/);
            if (cardsMatch) {
              cards = cardsMatch[1];
              console.log(`🔍 DEBUG: Cartas do perdedor ${player}: ${cards}`);
            }
          } else if (showedWonMatch) {
            // Procurar cartas no raw text para este jogador
            cards = this.findPlayerCardsInRaw(player);
            console.log(`🔍 DEBUG: Cartas do vencedor ${player} (extraídas do raw): ${cards}`);
          }
          
          actions.push({
            player: player,
            action: collectedMatch || wonMatch ? 'collected' : 'showed',
            amount: amount,
            street: 'summary',
            timestamp: startTimestamp++,
            cards: cards
          });
        }
      }
    }
  }

  /**
   * Extract SUMMARY lines from raw text
   */
  private extractSummaryLines(): string[] {
    const lines = this.rawText?.split('\n') || [];
    const summaryLines: string[] = [];
    let inSummary = false;
    
    for (const line of lines) {
      if (line.includes('*** SUMMARY ***')) {
        inSummary = true;
        continue;
      }
      
      if (inSummary) {
        if (line.trim() === '' || line.includes('***')) {
          break;
        }
        summaryLines.push(line);
      }
    }
    
    return summaryLines;
  }

  /**
   * Find player cards in raw text
   */
  private findPlayerCardsInRaw(playerName: string): string {
    const lines = this.rawText.split('\n');
    
    for (const line of lines) {
      if (line.includes('Dealt to') && line.includes(playerName)) {
        const match = line.match(/Dealt to [^(]+ \[([^\]]+)\]/);
        if (match) {
          return match[1];
        }
      }
    }
    
    return '';
  }

  /**
   * Calculate pot from actions and blinds
   */
  private calculatePot(actions: RiropoAction[], blinds: { small: number; big: number; ante?: number }): number {
    let pot = blinds.small + blinds.big;
    if (blinds.ante) pot += blinds.ante;

    for (const action of actions) {
      if (action.amount && action.action !== 'fold') {
        pot += action.amount;
      }
    }

    return pot;
  }

  /**
   * Get position name based on seat and button
   */
  private getPositionName(seat: number, buttonSeat: number, totalPlayers: number): string {
    const positions = ['BB', 'SB', 'BTN', 'CO', 'UTG+2', 'UTG+1', 'UTG'];
    const relativePosition = (seat - buttonSeat + totalPlayers) % totalPlayers;
    
    if (relativePosition < positions.length) {
      return positions[relativePosition];
    }
    
    return `Pos${relativePosition + 1}`;
  }

  /**
   * Get current hand as observable
   */
  getCurrentHand(): Observable<RiropoHand | null> {
    return this.currentHand$;
  }

  /**
   * Clear current hand
   */
  clearHand(): void {
    this.currentHandSubject.next(null);
  }
} 