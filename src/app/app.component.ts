import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PlatformSelectorComponent } from './components/platform-selector/platform-selector.component';
import { LogViewerComponent } from './components/log-viewer/log-viewer.component';
import { PlatformCredentialsComponent } from './components/platform-credentials/platform-credentials.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, PlatformSelectorComponent, LogViewerComponent, PlatformCredentialsComponent],
  template: `
    <div class="app-container">
      <header>
        <h1>Log Management System</h1>
      </header>
      
      <main>
        <app-platform-selector
          (platformSelected)="onPlatformSelect($event)"
        ></app-platform-selector>
        
        @if (selectedPlatform) {
          <section class="credentials-section">
            <h2>Platform Credentials</h2>
            <app-platform-credentials
              [platform]="selectedPlatform"
            ></app-platform-credentials>
          </section>
          
          <section class="logs-section">
            <h2>Logs</h2>
            <app-log-viewer
              [platform]="selectedPlatform"
            ></app-log-viewer>
          </section>
        }
      </main>
    </div>
  `,
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  selectedPlatform: string | null = null;

  onPlatformSelect(platform: string) {
    this.selectedPlatform = platform;
  }
} 