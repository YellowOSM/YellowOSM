import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { YellowmapComponent } from './yellowmap.component';

describe('YellowmapComponent', () => {
  let component: YellowmapComponent;
  let fixture: ComponentFixture<YellowmapComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ YellowmapComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(YellowmapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
