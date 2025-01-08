import { Component, Input, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  imports: [CommonModule],
  selector: 'app-message-modal',
  template: `
    <div class="modal" *ngIf="isOpen" (click)="closeOnBackdropClick($event)">
      <div class="modal-content">
        <span class="close" (click)="close()">&times;</span>
        <p>{{ message }}</p>
      </div>
    </div>
  `,
  styles: [`
    /* Modal Background */
    .modal {
      display: flex;
      align-items: center;
      justify-content: center;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.5);
    }

    /* Modal Content */
    .modal-content {
      background-color: #ffffff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      width: 90%;
      max-width: 600px;
      word-wrap: break-word;
      animation: fadeIn 0.3s ease-in-out;
    }

    /* Close Button */
    .close {
      color: #333;
      float: right;
      font-size: 1.5rem;
      font-weight: bold;
      cursor: pointer;
    }

    .close:hover {
      color: #000;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
      .modal-content {
        width: 95%;
        padding: 15px;
      }
      .close {
        font-size: 1.25rem;
      }
    }

    /* Fade-in Animation */
    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: scale(0.9);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }
  `]
})
export class MessageModalComponent {
  @Input() message: string = '';
  isOpen: boolean = false;

  open(message: string) {
    this.message = message;
    this.isOpen = true;
  }

  close() {
    this.isOpen = false;
  }

  closeOnBackdropClick(event: MouseEvent) {
    if ((event.target as HTMLElement).classList.contains('modal')) {
      this.close();
    }
  }
}
