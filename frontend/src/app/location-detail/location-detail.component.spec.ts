import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LocationDetailComponent } from './location-detail.component';

describe('LocationDetailComponent', () => {
  let component: LocationDetailComponent;
  let fixture: ComponentFixture<LocationDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LocationDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LocationDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
