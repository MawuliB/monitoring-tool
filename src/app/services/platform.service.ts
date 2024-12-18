import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Platform } from '../models/platform';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PlatformService {
  platforms = signal<Platform[]>([]);

  constructor(private http: HttpClient) {
    this.loadPlatforms();
  }

  private async loadPlatforms() {
    try {
      const response = await fetch(`${environment.apiUrl}/platforms`);
      const data = await response.json();
      this.platforms.set(data.platforms);
    } catch (error) {
      console.error('Error loading platforms:', error);
    }
  }
} 