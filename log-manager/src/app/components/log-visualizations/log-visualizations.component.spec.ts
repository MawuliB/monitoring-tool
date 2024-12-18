import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogVisualizationsComponent } from './log-visualizations.component';

describe('LogVisualizationsComponent', () => {
  let component: LogVisualizationsComponent;
  let fixture: ComponentFixture<LogVisualizationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LogVisualizationsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LogVisualizationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
