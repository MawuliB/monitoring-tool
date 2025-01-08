import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, ChartConfiguration, ChartType, registerables } from 'chart.js';
import { LogEntry } from '../../models/log.model';
import { BaseChartDirective } from 'ng2-charts';

@Component({
  selector: 'app-log-visualizations',
  standalone: true,
  imports: [
    CommonModule,
    BaseChartDirective
  ],
  template: `
    <div class="visualizations-container">
      <div class="chart-container">
        <h3>Log Levels Distribution</h3>
        <canvas baseChart
          [data]="logLevelChartData"
          [type]="logLevelChartType"
          [options]="chartOptions">
        </canvas>
      </div>
      <div class="summary-container">
        <h3>Summary</h3>
        <p><strong>Error Rate:</strong> {{ calculateErrorRate() }}%</p>
        <p><strong>Most Common Source:</strong> {{ getMostCommonSource() }}</p>
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
    .chart-container, .summary-container {
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

  constructor() {
    Chart.register(...registerables);
  }

  // Chart configuration
  logLevelChartData: ChartConfiguration['data'] = {
    labels: [],
    datasets: [
      {
        data: [],
        backgroundColor: ['#2ecc71', '#e74c3c', '#f1c40f', '#3498db'],
        hoverBackgroundColor: ['#27ae60', '#c0392b', '#f39c12', '#2980b9'],
      },
    ],
  };

  logLevelChartType: ChartType = 'pie';
  chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  ngOnChanges(changes: SimpleChanges) {
    if (changes['logs']) {
      this.updateChart();
    }
  }

  updateChart() {
    const logLevels = this.logs.reduce((acc, log) => {
      acc[log.level] = (acc[log.level] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    this.logLevelChartData.labels = Object.keys(logLevels);
    this.logLevelChartData.datasets[0].data = Object.values(logLevels);
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
      .sort(([, a], [, b]) => b - a)[0];

    return mostCommonSource;
  }
}