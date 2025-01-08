import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LogService } from '../../services/log.service';
import { LogEntry } from '../../models/log.model';
import { LogFilterComponent } from '../log-filter/log-filter.component';
import { LogTableComponent } from '../log-table/log-table.component';
import { LogVisualizationsComponent } from '../log-visualizations/log-visualizations.component';

interface LogFilter {
  startDate?: string;
  endDate?: string;
  level?: string;
  source?: string;
  platform?: string | null;
  [key: string]: any;
}

@Component({
  selector: 'app-log-viewer',
  standalone: true,
  imports: [
    CommonModule,
    LogFilterComponent,
    LogTableComponent,
    LogVisualizationsComponent
  ],
  template: `
    <div class="log-viewer">
      <app-log-filter (filterChange)="setFilters($event)"></app-log-filter>
      <div class="view-controls">
        <button 
          (click)="setView('table')"
          [class.active]="view === 'table'"
        >Table View</button>
        <button 
          (click)="setView('visual')"
          [class.active]="view === 'visual'"
        >Visual View</button>
      </div>
      
      <div class="content-area">
        <div *ngIf="loading" class="loading">
          <span>Loading...</span>
        </div>
        
        <div *ngIf="error" class="error">
          {{ error }}
        </div>

        <ng-container *ngIf="!loading && !error">
          <app-log-table 
            *ngIf="view === 'table'"
            [logs]="paginatedLogs"
          ></app-log-table>
          
          <app-log-visualizations 
            *ngIf="view === 'visual'"
            [logs]="logs"
          ></app-log-visualizations>

          <div *ngIf="view === 'table'" class="pagination">
            <button 
              [disabled]="currentPage === 1"
              (click)="setPage(currentPage - 1)"
            >Previous</button>
            <span>Page {{ currentPage }} of {{ totalPages }}</span>
            <button 
              [disabled]="currentPage === totalPages"
              (click)="setPage(currentPage + 1)"
            >Next</button>
          </div>
        </ng-container>
      </div>
    </div>
  `,
  styles: [`
    .log-viewer {
      padding: 1rem;
    }

    .view-controls {
      margin: 1rem 0;
      display: flex;
      gap: 0.5rem;
    }

    button {
      padding: 0.5rem 1rem;
      border: 1px solid #ddd;
      background: white;
      border-radius: 4px;
      cursor: pointer;
    }

    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    button.active {
      background: #007bff;
      color: white;
      border-color: #0056b3;
    }

    .loading, .error {
      padding: 1rem;
      text-align: center;
    }

    .pagination {
      margin-top: 1rem;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 1rem;
    }
  `]
})
export class LogViewerComponent implements OnInit {
  @Input() platform: string | null = null;
  logs: LogEntry[] = [];
  filters: LogFilter = {};
  view: 'table' | 'visual' = 'table';
  loading = false;
  error: string | null = null;

  // Pagination state
  currentPage = 1;
  pageSize = 50;
  
  constructor(private readonly logService: LogService) {}

  get totalPages(): number {
    return Math.ceil(this.logs.length / this.pageSize);
  }

  get paginatedLogs(): LogEntry[] {
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    return this.logs.slice(start, end);
  }

  async loadLogs() {
    if (!this.platform) return;
    
    try {
      this.loading = true;
      this.error = null;
      
      // Default to last hour if no dates are selected
      const now = new Date().toISOString();
      const oneHourAgo = new Date(Date.now() - 3600000).toISOString();
      console.log(this.filters);
      this.logs = await this.logService.fetchLogs(
        this.platform,
        this.filters.startDate ?? oneHourAgo,
        this.filters.endDate ?? now,
        this.filters['logType'] ?? '',
        this.filters['level'] ?? '',
        this.filters['keyword'] ?? ''
      );
      
      // Reset to first page when new logs are loaded
      this.currentPage = 1;
    } catch (err) {
      this.error = 'Failed to fetch logs. Please try again later.';
      console.error('Log fetch error:', err);
    } finally {
      this.loading = false;
    }
  }

  ngOnInit() {
    this.loadLogs();
  }

  setFilters(filters: LogFilter) {
    this.filters = filters;
    this.loadLogs();
  }

  setView(view: 'table' | 'visual') {
    this.view = view;
  }

  setPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }
}