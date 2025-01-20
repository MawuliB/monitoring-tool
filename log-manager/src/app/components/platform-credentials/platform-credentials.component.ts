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
        </ng-container>

        <ng-container *ngIf="platform === 'local' || platform === 'file'">
          <h3>No Credentials Required</h3>
          <p class="text-muted">
            No credentials are required for local or file platform.
          </p>
        </ng-container>

        <button type="submit" [disabled]="!credentialsForm.valid || loading" *ngIf="platform !== 'local' && platform !== 'file'">
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
  @Output() credentialsSaved = new EventEmitter<any>();
  
  credentialsForm: FormGroup;
  loading = false;
  platformConfig: any;

  constructor(
    private readonly fb: FormBuilder,
    private readonly apiService: ApiService
  ) {
    this.credentialsForm = this.fb.group({
      accessKeyId: [''],
      secretAccessKey: [''],
      region: [''],
    });
  }

  ngOnInit() {
    if (this.platform) {
      this.loadPlatformCredentials();
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['platform'] && !changes['platform'].firstChange) {
      this.loadPlatformCredentials();
    }
  }

  private async loadPlatformCredentials() {
    try {
      if(this.platform === 'aws') {
        this.updateFormValidation(true);
        this.getAndSetCredentials();
      }
    }
    catch (error) {
      console.error('Error loading platform credentials:', error);
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

  private async getAndSetCredentials() {
    try {
      const credentials = await this.apiService.getPlatformCredentials(this.platform).toPromise();
      // change field names of the credentials
      credentials['accessKeyId'] = credentials['access_key'];
      credentials['secretAccessKey'] = credentials['secret_key'];
      if (credentials) {
        this.credentialsForm.patchValue(credentials);
      }
    } catch (error) {
      console.error('Error getting platform credentials:', error);
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
        access_key: formValue.accessKeyId,
        secret_key: formValue.secretAccessKey,
        region: formValue.region
      };
    }
    
    return {};
  }
}