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
    console.log(environment.apiBaseUrl + '/geo58_to_coords/' + geo58hash);
    this.httpClient
      .get(environment.apiBaseUrl + '/geo58_to_coords/' + geo58hash)
      .subscribe(
        result => result['geo58'],
        error => console.log(error));
  }

}
