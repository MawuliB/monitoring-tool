import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output, Input } from '@angular/core';

@Component({
  imports: [CommonModule],
  selector: 'app-platform-selector',
  template: `
  <div class="platform-selector">
    <button
      *ngFor="let platform of platforms; trackBy: trackPlatform"
      (click)="selectPlatform(platform)"
      [class.selected]="selectedPlatform === platform"
    >
      {{ platform }}
    </button>
  </div>
`,
  styleUrls: ['./platform-selector.component.scss']
})
export class PlatformSelectorComponent {
  @Output() platformSelected = new EventEmitter<string>();
  @Input() selectedPlatform: string | null = null;

  platforms = ['aws', 'local'];

  selectPlatform(platform: string) {
    this.platformSelected.emit(platform);
  }

  trackPlatform(index: number, platform: string) {
    return platform;
  }
}