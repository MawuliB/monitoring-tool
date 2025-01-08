import { Component, Input, OnInit, OnChanges, SimpleChanges, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';

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
          <div class="form-group" *ngIf="logTypes.length > 0">
            <label>Log Groups</label>
            <select multiple formControlName="selectedLogGroups" class="form-control">
              <option *ngFor="let group of logTypes" [value]="group">
                {{ group }}
              </option>
            </select>
            <small class="text-muted">Hold Ctrl/Cmd to select multiple groups</small>
          </div>
        </ng-container>

        <ng-container *ngIf="platform === 'local'">
          <div class="form-group">
            <label>Log Type</label>
            <select formControlName="logType" class="form-control">
              <option *ngFor="let type of logTypes" [value]="type">
                {{ type }}
              </option>
            </select>
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
  logTypes: string[] = [];
  platformConfig: any;

  constructor(
    private readonly fb: FormBuilder,
    private readonly apiService: ApiService
  ) {
    this.credentialsForm = this.fb.group({
      accessKeyId: [''],
      secretAccessKey: [''],
      region: [''],
      logType: [''],
      selectedLogGroups: [[]]
    });
  }

  ngOnInit() {
    if (this.platform) {
      this.loadPlatformConfig();
    }
  }

  private async loadPlatformConfig() {
    try {
      const response = await this.apiService.getPlatforms().toPromise();
      this.platformConfig = response.platforms.find((p: any) => p.id === this.platform);
      
      if (this.platform === 'local') {
        this.logTypes = this.platformConfig.logTypes;
        this.updateFormValidation(false);
      } else if (this.platform === 'aws') {
        this.updateFormValidation(true);
        this.loadAwsLogGroups();
      }
    } catch (error) {
      console.error('Error loading platform config:', error);
    }
  }

  private updateFormValidation(requiresCredentials: boolean) {
    if (requiresCredentials) {
      this.credentialsForm.get('accessKeyId')?.setValidators([Validators.required]);
      this.credentialsForm.get('secretAccessKey')?.setValidators([Validators.required]);
      this.credentialsForm.get('region')?.setValidators([Validators.required]);
    } else {
      this.credentialsForm.get('accessKeyId')?.clearValidators();
      this.credentialsForm.get('secretAccessKey')?.clearValidators();
      this.credentialsForm.get('region')?.clearValidators();
    }
    this.credentialsForm.updateValueAndValidity();
  }

  private async loadAwsLogGroups() {
    try {
      const response: any = await this.apiService.getLogGroups(this.platform).toPromise();
      this.logTypes = response.logGroups;
    } catch (error) {
      console.error('Error loading AWS log groups:', error);
    }
  }

  async onSubmit() {
    if (this.credentialsForm.valid) {
      this.loading = true;
      try {
        const credentials = this.getCredentialsForPlatform();
        await this.apiService.savePlatformCredentials(this.platform, credentials).toPromise();
        this.credentialsSaved.emit();
      } catch (error) {
        console.error('Error saving credentials:', error);
      } finally {
        this.loading = false;
      }
    }
  }

  private getCredentialsForPlatform() {
    const formValue = this.credentialsForm.value;
    
    if (this.platform === 'aws') {
      return {
        access_key_id: formValue.accessKeyId,
        secret_access_key: formValue.secretAccessKey,
        region: formValue.region,
        path: formValue.selectedLogGroups
      };
    } else if (this.platform === 'local') {
      return {
        path: formValue.logType
      };
    }
    
    return {};
  }
}