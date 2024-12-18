import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LogEntry } from '../../models/log.model';

@Component({
  selector: 'app-log-visualizations',
  standalone: true,
  imports: [
    CommonModule
  ],
  template: `
    <div class="visualizations-container">
      <div class="chart-container">
        <h3>Log Levels Distribution</h3>
        <!-- Temporarily removed chart implementation -->
        <p>Chart visualization coming soon...</p>
      </div>
    </div>
  `,
  styles: [`
    .visualizations-container {
      padding: 1rem;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }

    .chart-container {
      background: white;
      padding: 1rem;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    h3 {
      margin: 0 0 1rem;
      color: #2c3e50;
      font-size: 1.1rem;
    }
  `]
})
export class LogVisualizationsComponent implements OnChanges {
  @Input() logs: LogEntry[] = [];

  ngOnChanges(changes: SimpleChanges) {
    if (changes['logs']) {
      // Removed updateCharts call
    }
  }

  calculateErrorRate(): string {
    if (!this.logs.length) return '0';
    const errorCount = this.logs.filter(log => log.level === 'ERROR').length;
    return ((errorCount / this.logs.length) * 100).toFixed(1);
  }

  getMostCommonSource(): string {
    if (!this.logs.length) return 'N/A';
    
    const sourceCounts = this.logs.reduce((acc, log) => {
      acc[log.source] = (acc[log.source] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const [mostCommonSource] = Object.entries(sourceCounts)
      .sort(([,a], [,b]) => b - a)[0];

    return mostCommonSource;
  }
}