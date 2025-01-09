import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly API_URL = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  savePlatformCredentials(platform: string, credentials: any): Observable<void> {
    return this.http.post<void>(`${this.API_URL}/credentials/${platform}`, credentials);
  }

  getPlatformCredentials(platform: string): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/credentials/${platform}`);
  }

  getLogGroups(platform: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_URL}/log-groups?platform=${platform}`);
  }

  getLogs(platform: string, startTime?: string, endTime?: string, logGroups?: string[], logType?: string): Observable<any> {
    let url = `${this.API_URL}/logs?platform=${platform}`;
    if (startTime) url += `&start_time=${startTime}`;
    if (endTime) url += `&end_time=${endTime}`;
    if (logGroups && logGroups.length) {
      logGroups.forEach(group => {
        url += `&log_groups=${encodeURIComponent(group)}`;
      });
    }
    if (logType) url += `&log_type=${encodeURIComponent(logType)}`;
    return this.http.get(url);
  }

  getPlatforms(): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/platforms`);
  }
}
