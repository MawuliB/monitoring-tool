import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlatformCredentialsComponent } from './platform-credentials.component';

describe('PlatformCredentialsComponent', () => {
  let component: PlatformCredentialsComponent;
  let fixture: ComponentFixture<PlatformCredentialsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PlatformCredentialsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PlatformCredentialsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
