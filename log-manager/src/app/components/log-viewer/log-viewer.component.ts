import { Component, Input, OnInit, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LogService } from '../../services/log.service';
import { LogEntry } from '../../models/log.model';
import { LogFilterComponent } from '../log-filter/log-filter.component';
import { LogTableComponent } from '../log-table/log-table.component';
import { LogVisualizationsComponent } from '../log-visualizations/log-visualizations.component';
import { Subscription } from 'rxjs';

interface LogFilter {
  startDate?: string;
  endDate?: string;
  level?: string;
  source?: string;
  platform?: string | null;
  logType?: string | null;
  logGroup?: string | null; 
  keyword?: string | null;
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
      <app-log-filter (filterChange)="setFilters($event)" [platform]="platform"></app-log-filter>
      <div class="view-controls">
        <button 
          (click)="setView('table')"
          [class.active]="view === 'table'"
        >Table View</button>
        <button 
          (click)="setView('visual')"
          [class.active]="view === 'visual'"
        >Visual View</button>
        <button 
          (click)="toggleLogTailing()"
          [class.active]="isTailingLogs"
        >{{ isTailingLogs ? 'Stop Tailing' : 'Start Tailing' }}</button>
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

          <div *ngIf="view === 'table' && !isTailingLogs" class="pagination">
            <button 
              [disabled]="currentPage === 1"
              (click)="setPage(1)"
            >&#171;</button>
            <button 
              [disabled]="currentPage === 1"
              (click)="setPage(currentPage - 1)"
            >Previous</button>
            <span>Page {{ currentPage }} of {{ totalPages }}</span>
            <button 
              [disabled]="currentPage === totalPages"
              (click)="setPage(currentPage + 1)"
            >Next</button>
            <button 
              [disabled]="currentPage === totalPages"
              (click)="setPage(totalPages)"
            >&#187;</button>
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
  private subscription: Subscription | undefined;
  @Input() platform: string = '';
  @Input() reloadLogGroups: boolean = false;

  logs: LogEntry[] = [];
  filters: LogFilter = {};
  view: 'table' | 'visual' = 'table';
  loading = false;
  error: string | null = null;
  isTailingLogs: boolean = false;
  logGroupName: string | null | undefined = undefined;

  // Pagination state
  currentPage = 1;
  pageSize = 50;
  
  constructor(
    private readonly logService: LogService
  ) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes['reloadLogGroups']) {
      if (!changes['reloadLogGroups'].firstChange) return;
      if (this.platform === 'aws') {
      this.loadLogs();
      this.reloadLogGroups = false;
      }
    }
  }

  get totalPages(): number {
    return Math.ceil(this.logs.length / this.pageSize);
  }

  get paginatedLogs(): LogEntry[] {
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    return this.logs.slice(start, end);
  }

  async loadLogs() {
    if (!this.platform || this.isTailingLogs) return;
    
    try {
      this.loading = true;
      this.error = null;
      
      // Default to last hour if no dates are selected
      const now = new Date().toISOString();
      const oneHourAgo = new Date(Date.now() - 3600000).toISOString();
      if(this.platform === 'aws' && !this.filters.logGroup) return;
      this.logs = await this.logService.fetchLogs(
        this.platform,
        this.filters.startDate ?? oneHourAgo,
        this.filters.endDate ?? now,
        this.filters['logType'] ?? '',
        this.filters['level'] ?? '',
        this.filters['logGroup'] ?? '',
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
    this.logGroupName = filters.logGroup ?? null; // Assign null if undefined
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

  toggleLogTailing() {
    this.isTailingLogs = !this.isTailingLogs;
    if (this.platform === 'aws') {
      if (this.isTailingLogs && this.logGroupName) {
      this.startTailingLogs();
    } else {
      this.stopTailingLogs();
    }
  } else if (this.platform === 'local') {
    console.warn('Local logs cannot be tailing.');
  }
  }

  startTailingLogs() {
    if (this.logGroupName) {
      this.subscription = this.logService.tailLogs(this.logGroupName).subscribe({
        next: (logEvent) => {
          if (!this.logs) {
            this.logs = [];
          }
          this.logs = [...this.logs, logEvent];
        },
        error: (error) => {
          console.error('Component error:', error);
        },
        complete: () => {
          console.log('Stream completed');
        }
      });
    } else {
      console.warn('Log group name is not defined.');
    }
  }
  
  stopTailingLogs() {
    if (this.subscription) {
      this.subscription.unsubscribe();
      console.log('Stopped tailing logs');
    }
  }

  // Always clean up when component is destroyed
  ngOnDestroy() {
    this.stopTailingLogs();
  }
}