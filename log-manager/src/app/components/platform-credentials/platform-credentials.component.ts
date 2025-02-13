import { Component, Input, OnInit, SimpleChanges, Output, EventEmitter } from '@angular/core';
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
            <input type="text" formControlName="access_key" />
          </div>
          <div class="form-group">
            <label>Secret Access Key</label>
            <input type="password" formControlName="secret_key" />
          </div>
          <div class="form-group">
            <label>Region</label>
            <input type="text" formControlName="region" />
          </div>
        </ng-container>

        <ng-container *ngIf="platform === 'azure'">
          <div class="form-group">
            <label>Tenant ID</label>
            <input type="text" formControlName="tenant_id" />
          </div>
          <div class="form-group">
            <label>Client ID</label>
            <input type="text" formControlName="client_id" />
          </div>
          <div class="form-group">
            <label>Client Secret</label>
            <input type="password" formControlName="client_secret" />
          </div>
        </ng-container>

        <ng-container *ngIf="platform === 'els'">
          <div class="form-group">
            <label>Host</label>
            <input type="text" formControlName="host" />
          </div>
          <div class="form-group">
            <label>API Key</label>
            <input type="password" formControlName="api_key" />
          </div>
        </ng-container>

        <ng-container *ngIf="platform === 'gcp'">
  <div class="form-group">
    <label>Project ID</label>
    <input type="text" formControlName="project_id" />
  </div>
  <div class="form-group">
    <label>Credentials Path (optional)</label>
    <input type="text" formControlName="credentials_path" />
    <small>For local development only</small>
  </div>
  <div class="form-group">
    <label>Service Account JSON file</label>
    <input 
    type="file" 
    formControlName="service_account_info"
    (change)="onFileChange($event)"
    accept=".json"
     />
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
  serviceAccountInfoContent: string = '';

  constructor(
    private readonly fb: FormBuilder,
    private readonly apiService: ApiService
  ) {
    this.credentialsForm = this.fb.group({});
    this.initializeForm();
  }

  ngOnInit() {
    if (this.platform) {
      this.loadPlatformCredentials();
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['platform']) {
      // NEW: Reset form when platform changes
      this.resetForm();
      if (!changes['platform'].firstChange) {
        this.loadPlatformCredentials();
      }
    }
  }

  onFileChange(event: any) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.readAsText(file);
      reader.onload = () => {
        const content = reader.result as string;
        this.serviceAccountInfoContent = content;
      };
      reader.onerror = (error) => {
        console.log(error);
      };
    }
  }

  private initializeForm() {
    this.credentialsForm = this.fb.group({
      access_key: [''],
      secret_key: [''],
      region: [''],
      project_id: [''],
      credentials_path: [''],
      service_account_info: [''],
      tenant_id: [''],
      client_id: [''],
      client_secret: [''],
      host: [''],
      api_key: [''],
    });
    
    // Initialize all controls with empty strings and no validators
    Object.keys(this.credentialsForm.controls).forEach(control => {
      this.credentialsForm.get(control)?.setValue('');
      this.credentialsForm.get(control)?.clearValidators();
    });
    this.credentialsForm.updateValueAndValidity();
  }

  private resetForm() {
    Object.keys(this.credentialsForm.controls).forEach(control => {
      this.credentialsForm.get(control)?.setValue('');
      this.credentialsForm.get(control)?.clearValidators();
    });
    this.credentialsForm.updateValueAndValidity();
  }

  private async loadPlatformCredentials() {
    try {
      this.updateFormValidation(this.platform);
      await this.getAndSetCredentials();
      this.credentialsForm.updateValueAndValidity();
    }
    catch (error) {
      console.error('Error loading platform credentials:', error);
    }
  }

  private updateFormValidation(platform: string) {
    switch (platform) {
      case 'aws':
        this.updateFormValidationForAws();
        break;
      case 'azure':
        this.updateFormValidationForAzure();
        break;
      case 'els':
        this.updateFormValidationForEls();
        break;
      case 'gcp':
        this.updateFormValidationForGcp();
        break;
      default:
        // Handle other platforms if necessary
        break;
    }
  }

  private resetValidation() {
    Object.keys(this.credentialsForm.controls).forEach(control => {
      this.credentialsForm.get(control)?.clearValidators();
      this.credentialsForm.get(control)?.updateValueAndValidity();
    });
  }

  private updateFormValidationForAws() {
    this.resetValidation();
      this.credentialsForm.get('access_key')?.setValidators([Validators.required]);
      this.credentialsForm.get('secret_key')?.setValidators([Validators.required]);
      this.credentialsForm.get('region')?.setValidators([Validators.required]);
    
    this.credentialsForm.updateValueAndValidity();
  }

  private updateFormValidationForAzure() {
    this.resetValidation();
      this.credentialsForm.get('tenant_id')?.setValidators([Validators.required]);
      this.credentialsForm.get('client_id')?.setValidators([Validators.required]);
      this.credentialsForm.get('client_secret')?.setValidators([Validators.required]);
    this.credentialsForm.updateValueAndValidity();
  }

  private updateFormValidationForGcp() {
    this.resetValidation();
      this.credentialsForm.get('project_id')?.setValidators([Validators.required]);
      this.credentialsForm.get('credentials_path')?.setValidators([]);
      this.credentialsForm.get('service_account_info')?.setValidators([Validators.required]);
    this.credentialsForm.updateValueAndValidity();
  }

  private updateFormValidationForEls(){
    this.resetValidation();
      this.credentialsForm.get('host')?.setValidators([Validators.required]);
      this.credentialsForm.get('api_key')?.setValidators([Validators.required]);
    this.credentialsForm.updateValueAndValidity();
  }

  private async getAndSetCredentials() {
    try {
      const credentials = await this.apiService.getPlatformCredentials(this.platform).toPromise();
      this.serviceAccountInfoContent = JSON.stringify(credentials.service_account_info, null, 2);
      credentials.service_account_info = null;
      this.resetForm();
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
        try {
          if (this.serviceAccountInfoContent && this.serviceAccountInfoContent !== '') {
        credentials.service_account_info = JSON.parse(this.serviceAccountInfoContent);
          }
        } catch (error) {
          console.error('Error parsing service account info:', error);
          return;
        }
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
        access_key: formValue.access_key,
        secret_key: formValue.secret_key,
        region: formValue.region
      };
    } else if (this.platform === 'azure') {
      return {
        tenant_id: formValue.tenant_id,
        client_id: formValue.client_id,
        client_secret: formValue.client_secret
      };
    } else if (this.platform === 'els') {
      return {
        host: formValue.host,
        api_key: formValue.api_key
      };
    } else if (this.platform === 'gcp') {
      return {
        project_id: formValue.project_id,
        credentials_path: formValue.credentials_path,
        service_account_info: formValue.service_account_info
      };
    }
    
    return {};
  }
}