import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { Geo58RedirectComponent } from './geo58-redirect.component';

describe('Geo58RedirectComponentComponent', () => {
  let component: Geo58RedirectComponent;
  let fixture: ComponentFixture<Geo58RedirectComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ Geo58RedirectComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(Geo58RedirectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
