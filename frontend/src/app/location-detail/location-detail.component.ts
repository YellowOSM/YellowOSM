import {Component, Input, OnChanges, OnInit, SimpleChanges} from '@angular/core';
import {Geo58Service} from '../services/geo58.service';
import {environment} from '../../environments/environment';
import Feature from 'ol/Feature';
import {toLonLat} from 'ol/proj';

@Component({
  selector: 'app-location-detail',
  templateUrl: './location-detail.component.html',
  styleUrls: ['./location-detail.component.scss']
})
export class LocationDetailComponent implements OnInit, OnChanges {
  static readonly PERMALINK_ID_PROPERTIES = [
    'amenity',
    'shop',
    'craft',
    'tourism',
    'leisure',
    'atm'
  ];

  @Input() feature: Feature = null;

  permalink = '';
  labels: object = {};

  constructor(
    private geo58service: Geo58Service
  ) {
  }

  ngOnInit() {
    this.parseFeature();
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.parseFeature();
  }

  private parseFeature() {
    if (!this.feature) {
      return;
    }
    this.labels = this.feature.values_.labels;
    const lonLat = toLonLat(this.feature.getGeometry().getCoordinates());
    this.permalink = this.getPermalink(lonLat);
  }

  private getPermalink(lonLat: object) {
    return '';
    let propertyUrlPart = '';

    for (let i = 0; i < LocationDetailComponent.PERMALINK_ID_PROPERTIES.length; i++) {
      const idValue = this.labels[LocationDetailComponent.PERMALINK_ID_PROPERTIES[i]];
      if (!idValue) {
        continue;
      }
      propertyUrlPart = LocationDetailComponent.PERMALINK_ID_PROPERTIES[i] + '=' + idValue;
      break;
    }

    if (!propertyUrlPart) {
      return '';
    }

    this.getShortLink(propertyUrlPart, lonLat);

    return window.location.origin + '/19/' +
      Number.parseFloat(lonLat[1].toFixed(5).toString()) + '/' +
      Number.parseFloat(lonLat[0].toFixed(5).toString()) + ';' + propertyUrlPart;
  }

  private getShortLink(propertyUrlPart, lonLat) {
    this.geo58service.toGeo58(19, lonLat[1], lonLat[0])
      .subscribe(hashUrl => {
          console.log(hashUrl);
          this.permalink = environment.shortLinkBaseUrl + '/' + hashUrl['g58'] + ';' + propertyUrlPart;
        },
        error => {
          console.error('Error: Geo58 link could net be retrieved');
          console.error(error);
        });
  }
}
