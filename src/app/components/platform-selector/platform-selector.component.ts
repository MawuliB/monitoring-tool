import { Component, EventEmitter, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PlatformService } from '../../services/platform.service';

@Component({
  selector: 'app-platform-selector',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="platform-selector">
      <h3>Select Platform</h3>
      <div class="platform-buttons">
        @for (platform of platforms(); track platform.id) {
          <button
            [class.active]="selectedPlatform === platform.id"
            (click)="selectPlatform(platform.id)"
          >
            {{ platform.name }}
          </button>
        }
      </div>
    </div>
  `,
  styles: [`
    .platform-buttons {
      display: flex;
      gap: 10px;
      margin-top: 10px;
    }

    button {
      padding: 10px 20px;
      border: 1px solid #ccc;
      border-radius: 4px;
      background: white;
      color: #333;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: #f0f0f0;
      }

      &.active {
        background: #007bff;
        color: white;
        border-color: #0056b3;
      }
    }
  `]
})
export class PlatformSelectorComponent {
  private platformService = inject(PlatformService);
  platforms = this.platformService.platforms;
  selectedPlatform: string | null = null;

  @Output() platformSelected = new EventEmitter<string>();

  selectPlatform(platformId: string) {
    this.selectedPlatform = platformId;
    this.platformSelected.emit(platformId);
  }
} 