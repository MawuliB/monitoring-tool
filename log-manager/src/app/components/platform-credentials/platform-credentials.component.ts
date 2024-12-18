import { Component, Input, OnInit, OnChanges, SimpleChanges, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { LogGroupService, LogGroup } from '../../services/log-group.service';

@Component({
  selector: 'app-platform-credentials',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="credentials-container">
      <form [formGroup]="credentialsForm" (ngSubmit)="onSubmit()">
        <ng-container *ngIf="platform === 'aws'">
          <div class="form-group">
            <label>Access Key ID</label>
            <input type="text" formControlName="accessKeyId" />
          </div>
          <div class="form-group">
            <label>Secret Access Key</label>
            <input type="password" formControlName="secretAccessKey" />
          </div>
          <div class="form-group">
            <label>Region</label>
            <input type="text" formControlName="region" />
          </div>

          <!-- Log Groups Selection -->
          <div class="form-group" *ngIf="logGroups.length > 0">
            <label>Log Groups</label>
            <select multiple formControlName="selectedLogGroups" class="form-control">
              <option *ngFor="let group of logGroups" [value]="group.name">
                {{ group.name }}
              </option>
            </select>
            <small class="text-muted">Hold Ctrl/Cmd to select multiple groups</small>
          </div>
        </ng-container>

        <ng-container *ngIf="platform === 'azure'">
          <div class="form-group">
            <label>Connection String</label>
            <input type="password" formControlName="connectionString" />
          </div>
        </ng-container>

        <button type="submit" [disabled]="!credentialsForm.valid || loading">
          {{ loading ? 'Saving...' : 'Save Credentials' }}
        </button>
      </form>
    </div>
  `,
  styles: [`
    .credentials-container {
      padding: 20px;
      max-width: 500px;
      margin: 0 auto;
    }
    .form-group {
      margin-bottom: 15px;
    }
    label {
      display: block;
      margin-bottom: 5px;
      font-weight: 500;
    }
    input, select {
      width: 100%;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    select[multiple] {
      height: 120px;
    }
    button {
      width: 100%;
      padding: 10px;
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:disabled {
      background-color: #ccc;
    }
    .text-muted {
      color: #6c757d;
      font-size: 0.875em;
    }
  `]
})
export class PlatformCredentialsComponent implements OnInit {
  @Input() platform: string = '';
  @Output() credentialsSaved = new EventEmitter<void>();
  
  credentialsForm: FormGroup;
  loading = false;
  logGroups: LogGroup[] = [];

  constructor(
    private fb: FormBuilder, 
    private apiService: ApiService,
    private logGroupService: LogGroupService
  ) {
    this.credentialsForm = this.fb.group({
      accessKeyId: ['', Validators.required],
      secretAccessKey: ['', Validators.required],
      region: ['', Validators.required],
      connectionString: [''],
      selectedLogGroups: [[]]
    });
  }

  ngOnInit() {
    this.loadLogGroups();
  }

  loadLogGroups() {
    if (this.platform === 'aws') {
      this.logGroupService.getLogGroups().subscribe({
        next: (response) => {
          this.logGroups = response.log_groups;
        },
        error: (error) => {
          console.error('Error loading log groups:', error);
        }
      });
    }
  }

  async onSubmit() {
    if (this.credentialsForm.valid) {
      this.loading = true;

      const credentials = {
        platform: this.platform,
        credentials: this.getCredentialsForPlatform()
      };

      try {
        await this.apiService.savePlatformCredentials(this.platform, credentials.credentials);
        this.loading = false;
        this.credentialsSaved.emit();
      } catch (error) {
        this.loading = false;
        console.error('Error saving credentials:', error);
      }
    }
  }

  private getCredentialsForPlatform() {
    if (this.platform === 'aws') {
      return {
        access_key: this.credentialsForm.get('accessKeyId')?.value,
        secret_key: this.credentialsForm.get('secretAccessKey')?.value,
        region: this.credentialsForm.get('region')?.value,
        log_groups: this.credentialsForm.get('selectedLogGroups')?.value || []
      };
    } else if (this.platform === 'azure') {
      return {
        connection_string: this.credentialsForm.get('connectionString')?.value
      };
    }
    return {};
  }
}