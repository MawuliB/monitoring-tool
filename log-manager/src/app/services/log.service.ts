import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LogService {
  private API_URL = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  async fetchLogs(filters: any): Promise<any[]> {
    try {
      return await firstValueFrom(
        this.http.get<any[]>(`${this.API_URL}/logs`, {
          params: filters
        })
      );
    } catch (error) {
      console.error('Error fetching logs:', error);
      return [];
    }
  }
}