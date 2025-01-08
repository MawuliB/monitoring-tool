import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { CommonModule } from '@angular/common';

import { AppComponent } from './app.component';
import { PlatformSelectorComponent } from './components/platform-selector/platform-selector.component';
import { LogViewerComponent } from './components/log-viewer/log-viewer.component';
import { PlatformCredentialsComponent } from './components/platform-credentials/platform-credentials.component';
import { LogFilterComponent } from './components/log-filter/log-filter.component';
import { LogTableComponent } from './components/log-table/log-table.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { LogVisualizationsComponent } from './components/log-visualizations/log-visualizations.component';
import { BaseChartDirective} from 'ng2-charts';
import { MessageModalComponent } from './message-modal/message-modal.component';

@NgModule({
  declarations: [
  ],
  imports: [
    BrowserModule,
    ReactiveFormsModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    CommonModule,
    PlatformSelectorComponent,
    LogViewerComponent,
    PlatformCredentialsComponent,
    LogFilterComponent,
    LogTableComponent,
    LoginComponent,
    RegisterComponent,
    DashboardComponent,
    LogVisualizationsComponent,
    BaseChartDirective,
    MessageModalComponent
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useValue: AuthInterceptor, multi: true }
  ],
  bootstrap: []
})
export class AppModule { }