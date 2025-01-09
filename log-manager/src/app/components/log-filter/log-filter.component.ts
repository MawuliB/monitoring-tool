import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';

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
  @Output() filterChange = new EventEmitter<any>();
  filterForm: FormGroup;

  constructor(private readonly fb: FormBuilder) {
    this.filterForm = this.fb.group({
      keyword: [''],
      startDate: [''],
      endDate: [''],
      level: ['']
    });

    // Emit changes whenever any form control changes
    this.filterForm.valueChanges.subscribe(value => {
      this.filterChange.emit(this.cleanFilters(value));
    });
  }

  onSubmit() {
    this.filterChange.emit(this.cleanFilters(this.filterForm.value));
  }

  resetFilters() {
    this.filterForm.reset();
    this.filterChange.emit({});
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
}