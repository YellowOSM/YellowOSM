import { TestBed } from '@angular/core/testing';

import { MatomoService } from './matomo.service';

describe('MatomoService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: MatomoService = TestBed.get(MatomoService);
    expect(service).toBeTruthy();
  });
});
