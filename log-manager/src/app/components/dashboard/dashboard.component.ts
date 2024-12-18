import { Component } from '@angular/core';
import { LogViewerComponent } from "../log-viewer/log-viewer.component";
import { PlatformCredentialsComponent } from "../platform-credentials/platform-credentials.component";
import { PlatformSelectorComponent } from "../platform-selector/platform-selector.component";
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  template: `
    <div class="dashboard-container">
      <app-platform-selector
        (platformSelected)="onPlatformSelect($event)"
      ></app-platform-selector>
      
      <ng-container *ngIf="selectedPlatform">
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
      </ng-container>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 1rem;
    }

    section {
      margin-top: 2rem;
    }

    h2 {
      margin-bottom: 1rem;
      color: #333;
    }
  `],
  imports: [CommonModule, PlatformSelectorComponent, PlatformCredentialsComponent, LogViewerComponent]
})
export class DashboardComponent {
  selectedPlatform: string | null = null;

  onPlatformSelect(platform: string) {
    this.selectedPlatform = platform;
  }
}
