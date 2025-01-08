import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CredentialsService {
  constructor(private readonly http: HttpClient) {}

  savePlatformCredentials(platform: string | null, data: any) {
    // Replace with your actual API endpoint
    const url = `/api/credentials/${platform}`;
    return this.http.post(url, data).toPromise();
  }
}