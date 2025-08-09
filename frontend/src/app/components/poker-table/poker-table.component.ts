import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PokerReplayerComponent } from '../poker-replayer/poker-replayer.component';

@Component({
  selector: 'app-poker-table',
  standalone: true,
  imports: [CommonModule, FormsModule, PokerReplayerComponent],
  templateUrl: './poker-table.component.html',
  styleUrls: ['./poker-table.component.scss']
})
export class PokerTableComponent implements OnInit {
  @Input() handReplay: any = null;
  
  showReplayer = false;
  handHistoryText = '';

  ngOnInit() {
    // Se há dados do handReplay, mostrar o replayer automaticamente
    if (this.handReplay) {
      this.showReplayer = true;
    }
  }

  loadHandFromDatabase() {
    if (this.handReplay) {
      this.showReplayer = true;
    }
  }

  loadHandHistory() {
    if (this.handHistoryText.trim()) {
      this.showReplayer = true;
    }
  }

  onHandComplete(event: any) {
    console.log('Hand replay completed:', event);
  }

  openFullscreen() {
    // Implementar tela cheia se necessário
    console.log('Fullscreen requested');
  }
}

