import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LogService {
  private readonly API_URL = 'http://localhost:8000';

  constructor(private readonly http: HttpClient) {}

  async  fetchLogs(platform: string, start_time: string, end_time: string, log_type: string, log_level: string, log_group: string, keyword: string): Promise<any[]> {
    const filters = {
      platform,
      start_time,
      end_time,
      log_type,
      log_level,
      log_group,
      keyword
    };
    try {
      const response = await firstValueFrom(
        this.http.get<{ logs: any[] }>(`${this.API_URL}/logs`, {
          params: filters
        })
      );
      return response.logs;
    } catch (error) {
      console.error('Error fetching logs:', error);
      return [];
    }
  }
}