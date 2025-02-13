import { Component, EventEmitter, Input, Output, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

@Component({
  selector: 'app-log-filter',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <form [formGroup]="filterForm" (ngSubmit)="onSubmit()" class="log-filter">
      <div class="filter-row">
        <div class="filter-group">
          <label>Date Range</label>
          <input
            type="datetime-local"
            formControlName="startDate"
            placeholder="Start Date"
          />
          <input
            type="datetime-local"
            formControlName="endDate"
            placeholder="End Date"
          />
        </div>
        
        <div class="filter-group">
          <label>Log Level</label>
          <select formControlName="level">
            <option value="">All Levels</option>
            <option value="INFO">Info</option>
            <option value="WARN">Warn</option>
            <option value="ERROR">Error</option>
            <option value="DEBUG">Debug</option>
          </select>
        </div>

        <div class="filter-group" *ngIf="platform === 'aws' || platform === 'azure' || platform === 'gcp' || platform === 'els'">
          <label>Log Group</label>
          <select formControlName="logGroup">
            <option *ngFor="let group of logGroups" [value]="group.name">
              {{group.name}}
            </option>
          </select>
        </div>

        <div class="filter-group" *ngIf="platform === 'local'">
          <label>Log Type</label>
          <select formControlName="logType">
            <option *ngFor="let type of logTypes" [value]="type">
              {{type}}
            </option>
          </select>
        </div>

        <div class="filter-group" *ngIf="platform === 'file'">
          <label>File Path</label>
          <input
            type="text"
            formControlName="filePath"
            placeholder="File Path"
          />
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-group search">
          <input
            type="text"
            formControlName="keyword"
            placeholder="Search logs..."
          />
        </div>
        
        <div class="filter-group">
          <button type="submit">Apply Filters</button>
          <button type="button" (click)="resetFilters()">Reset</button>
        </div>
      </div>
    </form>
  `,
  styles: [`
    .log-filter {
      padding: 1rem;
      background: #f5f5f5;
      border-radius: 4px;
    }

    .filter-row {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .filter-group {
      display: flex;
      gap: 0.5rem;
      align-items: center;
    }

    .filter-group.search {
      flex: 1;
    }

    input, select {
      padding: 0.5rem;
      border: 1px solid #ddd;
      border-radius: 4px;
    }

    input[type="text"] {
      width: 100%;
    }

    button {
      padding: 0.5rem 1rem;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }

    button[type="button"] {
      background: #6c757d;
    }

    button:hover {
      opacity: 0.9;
    }

    label {
      font-weight: 500;
      color: #495057;
    }
  `]
})
export class LogFilterComponent {
  @Input() platform: string = '';
  @Output() filterChange = new EventEmitter<any>();

  logGroups: any[] = [];
  logTypes: string[] = [];
  filterForm: FormGroup;

  private readonly keywordSubject = new Subject<string>();
  private readonly filePathSubject = new Subject<string>();

  constructor(
    private readonly fb: FormBuilder,
    private readonly apiService: ApiService
  ) {
    this.filterForm = this.fb.group({
      keyword: [''],
      startDate: [''],
      endDate: [''],
      level: [''],
      logGroup: [''],
      logType: ['syslog'],
      filePath: ['']
    });

    // Handle debounce for keyword
    this.keywordSubject.pipe(debounceTime(2000)).subscribe(keyword => {
      this.emitFilteredChange({ keyword });
    });

    // Handle debounce for filePath
    this.filePathSubject.pipe(debounceTime(2000)).subscribe(filePath => {
      this.emitFilteredChange({ filePath });
    });

    // Emit other filter changes immediately
    this.filterForm.valueChanges.subscribe(value => {
      const { keyword, filePath, ...otherValues } = value; // Exclude debounced fields
      this.emitFilteredChange(this.cleanFilters(otherValues));
    });
  }

  ngOnInit() {
    // Watch for keyword changes
    this.filterForm.get('keyword')?.valueChanges.subscribe(value => {
      this.keywordSubject.next(value);
    });

    // Watch for filePath changes
    this.filterForm.get('filePath')?.valueChanges.subscribe(value => {
      this.filePathSubject.next(value);
    });

    if (this.platform === 'aws' || this.platform === 'azure' || this.platform === 'gcp' || this.platform === 'els') {
      this.loadAwsLogGroups();
    } else if (this.platform === 'local') {
      this.loadLocalLogTypes();
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['platform'] && !changes['platform'].firstChange) {
      if (this.platform === 'aws' || this.platform === 'azure' || this.platform === 'gcp' || this.platform === 'els') {
        this.loadAwsLogGroups();
      } else if (this.platform === 'local') {
        this.loadLocalLogTypes();
      }
    }
  }

  onSubmit() {
    this.emitFilteredChange(this.cleanFilters(this.filterForm.value));
  }

  resetFilters() {
    this.filterForm.reset();
    this.emitFilteredChange({});
  }

  private async loadAwsLogGroups() {
    try {
      const response: any = await this.apiService.getLogGroups(this.platform).toPromise();
      this.logGroups = response.log_groups;
    } catch (error) {
      console.error('Error loading AWS log groups:', error);
    }
  }

  private async loadLocalLogTypes() {
    try {
      const response: any = await this.apiService.getLogTypes(this.platform).toPromise();
      this.logTypes = response.logTypes;
    } catch (error) {
      console.error('Error loading local log types:', error);
    }
  }

  private cleanFilters(filters: any) {
    // Remove empty values from filters
    return Object.entries(filters).reduce((acc: any, [key, value]) => {
      if (value !== '' && value !== null) {
        acc[key] = value;
      }
      return acc;
    }, {});
  }

  private emitFilteredChange(changes: any) {
    this.filterChange.emit(changes);
  }
}