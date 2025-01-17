import { Component } from '@angular/core';
import { AuthService } from './services/auth.service';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, CommonModule,],
  template: `
    <div class="app-container">
      <header>
        <h1>Log Management System</h1>
        <div class="auth-controls" *ngIf="authService.isAuthenticated()">
          <button (click)="logout()">Logout</button>
        </div>
      </header>
      
      <main>
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      padding: 1rem;
      background: linear-gradient(135deg, #ffffff, #f8f9fa, #faf0e6); 
      height: 100vh; 
      margin: 5px; 
      padding: 5px; 
      background-repeat: no-repeat; 
      background-attachment: fixed;
    }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #eee;
    }

    h1 {
      margin: 0;
      color: #333;
    }

    .auth-controls button {
      padding: 0.5rem 1rem;
      background-color: #dc3545;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }

    .auth-controls button:hover {
      background-color: #c82333;
    }

    main {
      margin-top: 1rem;
    }
  `]
})
export class AppComponent {
  constructor(
    public authService: AuthService,
    private readonly router: Router
  ) {}

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}