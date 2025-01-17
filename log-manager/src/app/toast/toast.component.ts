import { CommonModule } from '@angular/common';
import { Component, Input, NgZone } from '@angular/core';

@Component({
  selector: 'app-toast',
  imports: [CommonModule],
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.scss']
})
export class ToastComponent {
  message: string = '';
  type: 'success' | 'error' | 'warn' | 'info' = 'success';
  timer: any;
  open: boolean = false;

  constructor(private readonly ngZone: NgZone) { }

  openToast(message: string, type: 'success' | 'error' | 'warn' | 'info'): void {
    this.message = message;
    this.type = type;
    this.open = true;

    // Timeout to automatically close the toast after 5 seconds
    clearTimeout(this.timer);
    this.timer = this.ngZone.runOutsideAngular(() => {
      return setTimeout(() => {
        this.ngZone.run(() => {
          this.closeToast();
        });
      }, 5000);
    });
  }

  closeToast() {
    clearTimeout(this.timer);
    this.open = false;
  }
}
