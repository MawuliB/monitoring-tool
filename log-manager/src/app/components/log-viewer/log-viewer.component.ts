import { Component, Input, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LogService } from '../../services/log.service';
import { LogEntry } from '../../models/log.model';
import { LogFilterComponent } from '../log-filter/log-filter.component';
import { LogTableComponent } from '../log-table/log-table.component';
import { LogVisualizationsComponent } from '../log-visualizations/log-visualizations.component';
import { Subscription } from 'rxjs';
import { ToastComponent } from '../../toast/toast.component';

interface LogFilter {
  startDate?: string;
  endDate?: string;
  level?: string;
  source?: string;
  platform?: string | null;
  logType?: string | null;
  logGroup?: string | null; 
  filePath?: string | null;
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
    LogVisualizationsComponent,
    ToastComponent
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
        <div class="dropdown">
          <button class="dropbtn">Download Logs</button>
          <div class="dropdown-content">
            <a (click)="downloadLogs('json')">Download as JSON</a>
            <a (click)="downloadLogs('csv')">Download as CSV</a>
          </div>
        </div>
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
    <app-toast></app-toast>
  `,
  styles: [`
    .log-viewer {
      padding: 1rem;
    }

    .view-controls {
      margin: 1rem 1rem;
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
    .dropdown {
        position: relative;
        display: inline-block;
        margin-left: auto;
    }

    .dropbtn {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 10px 16px;
        font-size: 16px;
        border: none;
        cursor: pointer;
    }

    .dropdown-content {
        display: none;
        position: absolute;
        background-color: #f9f9f9;
        min-width: 160px;
        box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
        z-index: 1;
    }

    .dropdown:hover .dropdown-content {
        display: block;
    }

    .dropdown-content a {
        color: black;
        padding: 12px 16px;
        text-decoration: none;
        display: block;
    }

    .dropdown-content a:hover {
        background-color: #f1f1f1;
    }
  `]
})
export class LogViewerComponent implements OnInit {
  private subscription: Subscription | undefined;
  @Input() platform: string = localStorage.getItem('selectedPlatform') ?? 'aws';
  @Input() reloadLogGroups: boolean = false;
  @ViewChild(ToastComponent) toast!: ToastComponent;

  logs: LogEntry[] = [];
  filters: LogFilter = {};
  view: 'table' | 'visual' = 'table';
  loading = false;
  error: string | null = null;
  isTailingLogs: boolean = false;
  logGroupName: string = '';
  logType: string = 'syslog';
  filePath: string = '';

  // Pagination state
  currentPage = 1;
  pageSize = 50;
  
  constructor(
    private readonly logService: LogService
  ) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes['reloadLogGroups']) {
      if (!changes['reloadLogGroups'].firstChange) return;
      if (this.platform === 'aws' || this.platform === 'azure' || this.platform === 'gcp' || this.platform === 'els') {
        this.clearLogs();
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

  clearLogs() {
    this.logs = [];
  }

  async loadLogs() {
    if (!this.platform || this.isTailingLogs) {
      this.toast?.openToast('Please select a platform', 'error');
      return;
    }
    
    try {
      this.loading = true;
      this.error = null;
      
      // Default to last hour if no dates are selected
      const now = new Date().toISOString();
      const oneHourAgo = new Date(Date.now() - 3600000).toISOString();
      if((this.platform === 'aws' || this.platform === 'azure' || this.platform === 'gcp' || this.platform === 'els') && !this.filters.logGroup) {
         this.toast?.openToast('Please select a log group', 'error');
         return;
        }
      this.logs = await this.logService.fetchLogs(
        this.platform,
        this.filters.startDate ?? oneHourAgo,
        this.filters.endDate ?? now,
        this.filters['logType'] ?? '',
        this.filters['level'] ?? '',
        this.filters['logGroup'] ?? '',
        this.filters['keyword'] ?? '',
        this.filters['filePath'] ?? ''
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
    localStorage.setItem('logFilters', JSON.stringify(filters));
    const filtersFromStorage = JSON.parse(localStorage.getItem('logFilters') ?? '{}');
    this.logGroupName = filters.logGroup ?? filtersFromStorage.logGroup ?? '';
    this.logType = filters.logType ?? filtersFromStorage.logType ?? '';
    this.filePath = filters.filePath ?? filtersFromStorage.filePath ?? '';
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
  
    // Unified validation logic for platform-specific checks  
    const validationConditions: { [key: string]: boolean } = {
      aws: this.isTailingLogs && !!this.logGroupName?.trim(),
      local: this.isTailingLogs && !!this.logType?.trim(),
      file: this.isTailingLogs && !!this.filePath?.trim(),
    };
  
    if (!this.platform) {
      this.toast?.openToast('Platform Not Selected', 'error');
      return;
    }
  
    if (validationConditions[this.platform]) {
      this.startTailingLogs();
    } else {
      this.stopTailingLogs();
    }
  }
  
  startTailingLogs() {
    if (this.platform) {
      // Validate input before initiating the subscription
      if (
        (this.platform === 'aws' && !this.logGroupName?.trim()) ||
        (this.platform === 'local' && !this.logType?.trim()) ||
        (this.platform === 'file' && !this.filePath?.trim())
      ) {
        this.toast?.openToast('Please select or enter a log group, log type, or file path', 'error');
        return;
      }
  
      this.toast?.openToast(`Tailing logs for ${this.platform}`, 'info');
  
      this.subscription = this.logService.tailLogs(this.logGroupName, this.platform, this.logType, this.filePath).subscribe({
        next: (logEvent) => {
          this.logs = [...(this.logs || []), logEvent];
        },
        error: (error) => {
          this.toast?.openToast('Error tailing logs', 'error');
          console.error('Component error:', error);
        },
        complete: () => {
          console.log('Stream completed');
        },
      });
    } else {
      console.warn('Platform is not defined.');
    }
  }
  
  stopTailingLogs() {
    if (this.subscription) {
      this.subscription.unsubscribe();
      this.isTailingLogs = false;
      this.toast?.openToast('Stopped tailing logs', 'info');
      console.log('Stopped tailing logs');
    }
  }
  

  downloadLogs(format: 'json' | 'csv') {
    const data = this.logs; // Assuming logs is the array of log entries
    let blob: Blob;
    let fileName: string;

    if (format === 'json') {
        const json = JSON.stringify(data, null, 2);
        blob = new Blob([json], { type: 'application/json' });
        fileName = 'logs.json';
    } else if (format === 'csv') {
        const csv = this.convertToCSV(data);
        blob = new Blob([csv], { type: 'text/csv' });
        fileName = 'logs.csv';
    } else {
        return; // Early return if format is not recognized
    }

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  convertToCSV(data: any[]): string {
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(item => Object.values(item).join(','));
    return `${headers}\n${rows.join('\n')}`;
  }

  // Always clean up when component is destroyed
  ngOnDestroy() {
    this.stopTailingLogs();
  }
}