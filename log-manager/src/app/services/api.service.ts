import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly API_URL = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  async savePlatformCredentials(platform: string, credentials: any): Promise<void> {
    await firstValueFrom(
      this.http.post(`${this.API_URL}/credentials/${platform}`, credentials)
    );
  }

  async getPlatformCredentials(platform: string): Promise<any> {
    return firstValueFrom(
      this.http.get(`${this.API_URL}/credentials/${platform}`)
    );
  }
}
