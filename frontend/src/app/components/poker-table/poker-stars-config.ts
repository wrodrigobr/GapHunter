/**
 * Configuração da Mesa de Poker inspirada no PokerStars
 * Incorpora elementos de projetos open source populares
 */

export interface PokerTableConfig {
  // Configurações visuais
  theme: 'pokerstars' | 'classic' | 'modern' | 'dark';
  tableColor: string;
  cardStyle: 'standard' | 'pokerstars' | 'casino';
  chipStyle: '3d' | 'flat' | 'realistic';
  
  // Animações
  animations: {
    cardFlip: boolean;
    chipFlying: boolean;
    playerPulse: boolean;
    dealerRotation: boolean;
  };
  
  // Posicionamento dos jogadores
  playerPositions: PlayerPosition[];
  
  // Efeitos sonoros (opcional)
  soundEffects: {
    cardFlip: string;
    chipSound: string;
    winSound: string;
  };
}

export interface PlayerPosition {
  seat: number;
  x: number;
  y: number;
  rotation: number;
}

// Configuração padrão inspirada no PokerStars
export const POKERSTARS_CONFIG: PokerTableConfig = {
  theme: 'pokerstars',
  tableColor: '#2d7d2d',
  cardStyle: 'pokerstars',
  chipStyle: '3d',
  
  animations: {
    cardFlip: true,
    chipFlying: true,
    playerPulse: true,
    dealerRotation: true
  },
  
  playerPositions: [
    { seat: 1, x: 50, y: 90, rotation: 0 },    // Bottom center (Hero)
    { seat: 2, x: 25, y: 75, rotation: 15 },   // Bottom left
    { seat: 3, x: 8, y: 45, rotation: 45 },    // Middle left
    { seat: 4, x: 15, y: 12, rotation: 75 },   // Top left
    { seat: 5, x: 50, y: 2, rotation: 90 },    // Top center
    { seat: 6, x: 85, y: 12, rotation: 105 },  // Top right
    { seat: 7, x: 92, y: 45, rotation: 135 },  // Middle right
    { seat: 8, x: 75, y: 75, rotation: 165 },  // Bottom right
    { seat: 9, x: 65, y: 90, rotation: 180 }   // Bottom right center
  ],
  
  soundEffects: {
    cardFlip: 'assets/sounds/card-flip.mp3',
    chipSound: 'assets/sounds/chip-sound.mp3',
    winSound: 'assets/sounds/win-sound.mp3'
  }
};

// Configuração clássica
export const CLASSIC_CONFIG: PokerTableConfig = {
  theme: 'classic',
  tableColor: '#1e6b1e',
  cardStyle: 'standard',
  chipStyle: 'flat',
  
  animations: {
    cardFlip: false,
    chipFlying: false,
    playerPulse: true,
    dealerRotation: false
  },
  
  playerPositions: [
    { seat: 1, x: 50, y: 85, rotation: 0 },
    { seat: 2, x: 20, y: 70, rotation: 0 },
    { seat: 3, x: 10, y: 40, rotation: 0 },
    { seat: 4, x: 20, y: 15, rotation: 0 },
    { seat: 5, x: 50, y: 5, rotation: 0 },
    { seat: 6, x: 80, y: 15, rotation: 0 },
    { seat: 7, x: 90, y: 40, rotation: 0 },
    { seat: 8, x: 80, y: 70, rotation: 0 },
    { seat: 9, x: 70, y: 85, rotation: 0 }
  ],
  
  soundEffects: {
    cardFlip: '',
    chipSound: '',
    winSound: ''
  }
};

// Configuração moderna
export const MODERN_CONFIG: PokerTableConfig = {
  theme: 'modern',
  tableColor: '#1a1a2e',
  cardStyle: 'standard', // Corrigido aqui
  chipStyle: 'realistic',
  
  animations: {
    cardFlip: true,
    chipFlying: true,
    playerPulse: true,
    dealerRotation: true
  },
  
  playerPositions: [
    { seat: 1, x: 50, y: 88, rotation: 0 },
    { seat: 2, x: 22, y: 72, rotation: 12 },
    { seat: 3, x: 6, y: 42, rotation: 35 },
    { seat: 4, x: 12, y: 10, rotation: 65 },
    { seat: 5, x: 50, y: 0, rotation: 90 },
    { seat: 6, x: 88, y: 10, rotation: 115 },
    { seat: 7, x: 94, y: 42, rotation: 145 },
    { seat: 8, x: 78, y: 72, rotation: 168 },
    { seat: 9, x: 68, y: 88, rotation: 180 }
  ],
  
  soundEffects: {
    cardFlip: 'assets/sounds/modern-card.mp3',
    chipSound: 'assets/sounds/modern-chip.mp3',
    winSound: 'assets/sounds/modern-win.mp3'
  }
};

// Elementos visuais do PokerStars
export const POKERSTARS_ELEMENTS = {
  // Cores
  colors: {
    primary: '#00d4aa',
    secondary: '#ffd700',
    accent: '#e74c3c',
    background: '#2d7d2d',
    text: '#ffffff',
    shadow: '#0a4a0a'
  },
  
  // Gradientes
  gradients: {
    table: 'radial-gradient(ellipse at center, #2d7d2d 0%, #1e6b1e 40%, #0f5a0f 70%, #0a4a0a 100%)',
    card: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
    chip: 'linear-gradient(135deg, #d4af37 0%, #ffd700 50%, #d4af37 100%)',
    button: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)'
  },
  
  // Sombras
  shadows: {
    table: 'inset 0 0 80px rgba(0, 0, 0, 0.5), 0 0 60px rgba(0, 0, 0, 0.7)',
    card: '0 6px 16px rgba(0, 0, 0, 0.4), 0 3px 6px rgba(0, 0, 0, 0.3)',
    chip: '0 4px 12px rgba(0, 0, 0, 0.3)',
    player: '0 8px 20px rgba(0, 0, 0, 0.4)'
  },
  
  // Animações
  animations: {
    cardFlip: 'cardFlip 1s cubic-bezier(0.4, 0, 0.2, 1)',
    chipFly: 'chipFly 1.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    playerPulse: 'activePulse 2s ease-in-out infinite',
    dealerRotate: 'dealerRotate 3s linear infinite'
  }
};

// Elementos de projetos open source populares
export const OPEN_SOURCE_ELEMENTS = {
  // Poker.js elements
  pokerJS: {
    cardBackPattern: '🂠',
    suitSymbols: {
      's': '♠',
      'h': '♥', 
      'd': '♦',
      'c': '♣'
    },
    rankSymbols: {
      'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T',
      '9': '9', '8': '8', '7': '7', '6': '6', '5': '5', '4': '4', '3': '3', '2': '2'
    }
  },
  
  // React Poker Table elements
  reactPoker: {
    chipColors: {
      white: '#ffffff',
      red: '#e74c3c',
      blue: '#3498db',
      green: '#27ae60',
      black: '#2c3e50',
      purple: '#9b59b6',
      orange: '#e67e22',
      yellow: '#f1c40f'
    },
    chipValues: {
      white: 1,
      red: 5,
      blue: 10,
      green: 25,
      black: 100,
      purple: 500,
      orange: 1000,
      yellow: 5000
    }
  },
  
  // PokerStars Clone elements
  pokerStarsClone: {
    tablePattern: 'repeating-linear-gradient(45deg, transparent, transparent 3px, rgba(255, 255, 255, 0.03) 3px, rgba(255, 255, 255, 0.03) 6px)',
    dealerButtonStyle: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
    blindIndicators: {
      small: 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)',
      big: 'linear-gradient(135deg, #e67e22 0%, #f39c12 100%)'
    }
  }
};

// Funções utilitárias
export class PokerTableUtils {
  
  /**
   * Aplica configuração de tema
   */
  static applyTheme(config: PokerTableConfig): void {
    const root = document.documentElement;
    
    // Aplicar variáveis CSS
    root.style.setProperty('--table-color', config.tableColor);
    root.style.setProperty('--primary-color', POKERSTARS_ELEMENTS.colors.primary);
    root.style.setProperty('--secondary-color', POKERSTARS_ELEMENTS.colors.secondary);
    
    // Aplicar classes de tema
    document.body.className = `poker-theme-${config.theme}`;
  }
  
  /**
   * Calcula posição do jogador baseada na configuração
   */
  static getPlayerPosition(seat: number, config: PokerTableConfig): PlayerPosition {
    return config.playerPositions.find(pos => pos.seat === seat) || 
           { seat, x: 50, y: 50, rotation: 0 };
  }
  
  /**
   * Formata carta no estilo especificado
   */
  static formatCard(card: string, style: string): string {
    if (!card) return '';
    const rank = card.charAt(0);
    const suit = card.charAt(1);
    switch (style) {
      case 'pokerstars':
        return `${OPEN_SOURCE_ELEMENTS.pokerJS.rankSymbols[rank as keyof typeof OPEN_SOURCE_ELEMENTS.pokerJS.rankSymbols]}${OPEN_SOURCE_ELEMENTS.pokerJS.suitSymbols[suit as keyof typeof OPEN_SOURCE_ELEMENTS.pokerJS.suitSymbols]}`;
      case 'modern':
        return `${rank}${suit.toUpperCase()}`;
      default:
        return `${rank}${OPEN_SOURCE_ELEMENTS.pokerJS.suitSymbols[suit as keyof typeof OPEN_SOURCE_ELEMENTS.pokerJS.suitSymbols]}`;
    }
  }
  
  /**
   * Obtém cor da ficha baseada no valor
   */
  static getChipColor(value: number): string {
    const colors = OPEN_SOURCE_ELEMENTS.reactPoker.chipColors;
    const values = OPEN_SOURCE_ELEMENTS.reactPoker.chipValues;
    for (const color of Object.keys(values) as Array<keyof typeof colors>) {
      if (value >= values[color]) {
        return colors[color];
      }
    }
    return colors.white;
  }
  
  /**
   * Reproduz efeito sonoro
   */
  static playSound(soundType: string, config: PokerTableConfig): void {
    const sound = config.soundEffects[soundType as keyof typeof config.soundEffects];
    if (sound) {
      const audio = new Audio(sound);
      audio.volume = 0.3;
      audio.play().catch(() => {
        // Ignorar erros de áudio
      });
    }
  }
} 