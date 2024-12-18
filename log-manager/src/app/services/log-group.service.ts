import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface LogGroup {
  name: string;
  arn: string;
  storedBytes: number;
  creationTime: string;
}

@Injectable({
  providedIn: 'root'
})
export class LogGroupService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private readonly http: HttpClient) { }

  getLogGroups(): Observable<{ log_groups: LogGroup[] }> {
    return this.http.get<{ log_groups: LogGroup[] }>(`${this.apiUrl}/log-groups`);
  }
}
