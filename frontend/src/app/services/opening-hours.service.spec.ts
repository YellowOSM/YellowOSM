import { TestBed } from '@angular/core/testing';

import { OpeningHoursService } from './opening-hours.service';

describe('OpeningHoursService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: OpeningHoursService = TestBed.get(OpeningHoursService);
    expect(service).toBeTruthy();
  });
});
