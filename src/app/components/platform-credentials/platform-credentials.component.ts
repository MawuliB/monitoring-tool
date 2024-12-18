import { Component, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { CredentialService } from '../../services/credential.service';

@Component({
  selector: 'app-platform-credentials',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <form [formGroup]="credentialForm" (ngSubmit)="onSubmit()">
      @if (platform === 'aws') {
        <input formControlName="access_key" placeholder="Access Key" />
        <input 
          formControlName="secret_key" 
          type="password" 
          placeholder="Secret Key" 
        />
        <input formControlName="region" placeholder="Region" />
      }
      
      @if (platform === 'local') {
        <input formControlName="path" placeholder="Log File Path" />
      }

      <button type="submit" [disabled]="credentialForm.invalid || saving()">
        {{ saving() ? 'Saving...' : 'Save Credentials' }}
      </button>

      @if (error()) {
        <div class="error">{{ error() }}</div>
      }
    </form>
  `,
  styles: [`
    form {
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 400px;
    }

    input {
      padding: 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }

    .error {
      color: #dc3545;
      font-size: 0.875rem;
      margin-top: 5px;
    }
  `]
})
export class PlatformCredentialsComponent {
  @Input() platform!: string;
  
  private fb = inject(FormBuilder);
  private credentialService = inject(CredentialService);
  
  saving = signal(false);
  error = signal<string | null>(null);
  
  credentialForm = this.fb.group({
    access_key: [''],
    secret_key: [''],
    region: [''],
    path: ['']
  });

  async onSubmit() {
    if (this.credentialForm.valid) {
      try {
        this.saving.set(true);
        this.error.set(null);
        
        await this.credentialService.saveCredentials(
          this.platform,
          this.credentialForm.value
        );
        
        // Reset form after successful save
        this.credentialForm.reset();
      } catch (err) {
        this.error.set('Failed to save credentials');
        console.error(err);
      } finally {
        this.saving.set(false);
      }
    }
  }
} 