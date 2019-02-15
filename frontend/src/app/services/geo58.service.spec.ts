import { TestBed } from '@angular/core/testing';

import { Geo58Service } from './geo58.service';

describe('Geo58Service', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: Geo58Service = TestBed.get(Geo58Service);
    expect(service).toBeTruthy();
  });
});
