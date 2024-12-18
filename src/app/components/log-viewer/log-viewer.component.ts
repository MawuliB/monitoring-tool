import { Component, Input, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LogFilterComponent } from '../log-filter/log-filter.component';
import { LogTableComponent } from '../log-table/log-table.component';
import { LogVisualizationsComponent } from '../log-visualizations/log-visualizations.component';
import { LogService } from '../../services/log.service';

@Component({
  selector: 'app-log-viewer',
  standalone: true,
  imports: [CommonModule, LogFilterComponent, LogTableComponent, LogVisualizationsComponent],
  template: `
    <div class="log-viewer">
      <app-log-filter (filterChange)="handleFilterChange($event)"></app-log-filter>
      
      <div class="view-controls">
        <button (click)="view.set('table')" [class.active]="view() === 'table'">
          Table View
        </button>
        <button (click)="view.set('visual')" [class.active]="view() === 'visual'">
          Visualizations
        </button>
      </div>

      @if (loading()) {
        <div>Loading logs...</div>
      } @else if (error()) {
        <div class="error">{{ error() }}</div>
      } @else {
        @if (view() === 'table') {
          <app-log-table [logs]="logs()"></app-log-table>
        } @else {
          <app-log-visualizations [logs]="logs()"></app-log-visualizations>
        }
      }
    </div>
  `,
  styles: [`
    .log-viewer {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .view-controls {
      display: flex;
      gap: 10px;
    }

    .error {
      color: #dc3545;
      padding: 10px;
      border: 1px solid #dc3545;
      border-radius: 4px;
      background: #f8d7da;
    }
  `]
})
export class LogViewerComponent {
  @Input() platform!: string;
  
  private logService = inject(LogService);
  
  view = signal<'table' | 'visual'>('table');
  logs = signal<any[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);
  filters = signal<any>({});

  ngOnInit() {
    this.loadLogs();
  }

  async loadLogs() {
    try {
      this.loading.set(true);
      this.error.set(null);
      const results = await this.logService.fetchLogs({
        ...this.filters(),
        platform: this.platform
      });
      this.logs.set(results);
    } catch (err) {
      this.error.set('Failed to fetch logs');
      console.error(err);
    } finally {
      this.loading.set(false);
    }
  }

  handleFilterChange(newFilters: any) {
    this.filters.set(newFilters);
    this.loadLogs();
  }
} 