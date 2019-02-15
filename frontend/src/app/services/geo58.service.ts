import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class Geo58Service {

  constructor(
    private httpClient: HttpClient
  ) {
  }

  toZoomLatLon(geo58hash: string) {
    return this.httpClient.get(environment.apiBaseUrl + '/geo58_to_coords/' + geo58hash);
  }

  toGeo58(zoom: number, x: number, y: number) {
    return this.httpClient.get(environment.apiBaseUrl + '/coords_to_geo58/' + zoom + '/' + x + '/' + y);
  }
}
