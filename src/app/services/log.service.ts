import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LogService {
  constructor(private http: HttpClient) {}

  async fetchLogs(filters: any): Promise<any[]> {
    try {
      const response = await fetch(`${environment.apiUrl}/logs`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters)
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching logs:', error);
      return [];
    }
  }
} 