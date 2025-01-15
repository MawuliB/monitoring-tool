import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom, Observable, switchMap } from 'rxjs';
import { LogEntry } from '../models/log.model';
import { AuthService } from './auth.service';
import { EventSourcePolyfill } from 'event-source-polyfill';

@Injectable({
  providedIn: 'root'
})
export class LogService {
  private readonly API_URL = 'http://localhost:8000';
  private readonly authService = inject(AuthService);

  constructor(private readonly http: HttpClient) {}

  async fetchLogs(platform: string, start_time: string, end_time: string, log_type: string, log_level: string, log_group: string, keyword: string): Promise<any[]> {
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

  tailLogs(logGroupName: string): Observable<any> {
    const token = this.authService.getToken();
    return new Observable(observer => {
      console.log('Starting EventSource connection...');
      
      const eventSource = new EventSourcePolyfill(
        `${this.API_URL}/logs/tail/aws?log_group_name=${logGroupName}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
  
      // Add onopen handler to verify connection
      eventSource.onopen = (event) => {
        console.log('EventSource connected!', event);
      };
  
      eventSource.onmessage = (event) => {  
        try {
          const logEvent = JSON.parse(event.data);
          observer.next(logEvent);
        } catch (error) {
          console.error('Error parsing event data:', error);
          console.log('Problematic data:', event.data);
        }
      };
  
      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        observer.error(error);
      };
  
      return () => {
        console.log('Closing EventSource connection...');
        eventSource.close();
      };
    });
  }
  
}