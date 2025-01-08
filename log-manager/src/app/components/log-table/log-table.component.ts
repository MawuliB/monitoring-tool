import { Component, Input, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LogEntry } from '../../models/log.model';
import { MessageModalComponent } from '../../message-modal/message-modal.component';


@Component({
  selector: 'app-log-table',
  standalone: true,
  imports: [CommonModule, MessageModalComponent],
  template: `
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th (click)="sort('timestamp')">
              Timestamp
              <span class="sort-icon" *ngIf="sortField === 'timestamp'">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th (click)="sort('level')">
              Level
              <span class="sort-icon" *ngIf="sortField === 'level'">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th (click)="sort('source')">
              Source
              <span class="sort-icon" *ngIf="sortField === 'source'">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let log of sortedLogs; let i = index">
            <td>{{ formatDate(log.timestamp) }}</td>
            <td>
              <span [class]="'level-badge ' + log.level.toLowerCase()">
                {{ log.level }}
              </span>
            </td>
            <td>{{ log.source }}</td>
            <td class="message-cell" (click)="openMessage(log.message)" title="Click to see full message">{{ log.message }}</td>
          </tr>
          <tr *ngIf="!logs.length">
            <td colspan="4" class="no-data">No logs found</td>
          </tr>
        </tbody>
      </table>
    </div>
    <app-message-modal #messageModal></app-message-modal>
  `,
  styles: [`
    .table-container {
      overflow-x: auto;
      white-space: nowrap;
      margin: 1rem 0;
      background: white;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 800px;
    }

    th, td {
      padding: 0.75rem 1rem;
      text-align: left;
      border-bottom: 1px solid #eee;
    }

    th {
      background: #f8f9fa;
      font-weight: 600;
      cursor: pointer;
      user-select: none;
    }

    th:hover {
      background: #e9ecef;
    }

    .message-cell {
      max-width: 400px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      cursor: pointer;
    }

    .level-badge {
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.875rem;
      font-weight: 500;
    }

    .level-badge.info {
      background: #cce5ff;
      color: #004085;
    }

    .level-badge.warning {
      background: #fff3cd;
      color: #856404;
    }

    .level-badge.error {
      background: #f8d7da;
      color: #721c24;
    }

    .level-badge.debug {
      background: #d1ecf1;
      color: #0c5460;
    }

    .sort-icon {
      margin-left: 0.5rem;
    }

    .no-data {
      text-align: center;
      color: #6c757d;
      padding: 2rem !important;
    }

    tr:hover {
      background: #f8f9fa;
    }
  `]
})
export class LogTableComponent {
  @Input() logs: LogEntry[] = [];
  sortField: keyof LogEntry = 'timestamp';
  sortOrder: 'asc' | 'desc' = 'desc';
  @ViewChild('messageModal') messageModal!: MessageModalComponent;

  get sortedLogs(): LogEntry[] {
    return [...this.logs].sort((a, b) => {
      const aValue = a[this.sortField];
      const bValue = b[this.sortField];
      
      if (aValue < bValue) return this.sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return this.sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }

  sort(field: keyof LogEntry) {
    if (this.sortField === field) {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortField = field;
      this.sortOrder = 'asc';
    }
  }

  formatDate(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  openMessage(message: string) {
    this.messageModal.open(message);
  }
}