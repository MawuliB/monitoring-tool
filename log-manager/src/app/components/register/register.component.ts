import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterLink, CommonModule],
  template: `
    <div class="register-container">
      <h2>Register</h2>
      <form (ngSubmit)="onSubmit()" #registerForm="ngForm">
        <div class="form-group">
          <label for="username">Username:</label>
          <input
            type="text"
            id="username"
            name="username"
            [(ngModel)]="username"
            required
          />
        </div>
        <div class="form-group">
          <label for="email">Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            [(ngModel)]="email"
            required
            email
          />
        </div>
        <div class="form-group">
          <label for="password">Password:</label>
          <input
            type="password"
            id="password"
            name="password"
            [(ngModel)]="password"
            required
            minlength="6"
          />
        </div>
        <button type="submit" [disabled]="!registerForm.form.valid">
          Register
        </button>
        <p *ngIf="error" class="error">{{ error }}</p>
      </form>
      <p>
        Already have an account?
        <a routerLink="/login">Login here</a>
      </p>
    </div>
  `,
  styles: [`
    .register-container {
      max-width: 400px;
      margin: 2rem auto;
      padding: 2rem;
      border: 1px solid #ccc;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .form-group {
      margin-bottom: 1rem;
    }

    label {
      display: block;
      margin-bottom: 0.5rem;
    }

    input {
      width: 100%;
      padding: 0.5rem;
      border: 1px solid #ccc;
      border-radius: 4px;
    }

    button {
      width: 100%;
      padding: 0.75rem;
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }

    button:disabled {
      background-color: #ccc;
      cursor: not-allowed;
    }

    .error {
      color: red;
      margin-top: 1rem;
    }

    a {
      color: #007bff;
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
    }
  `]
})
export class RegisterComponent {
  username = '';
  email = '';
  password = '';
  error = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit() {
    this.error = '';
    this.authService.register({
      username: this.username,
      email: this.email,
      password: this.password
    }).subscribe({
      next: () => {
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.error = err.error?.message || 'Registration failed. Please try again.';
      }
    });
  }
}
