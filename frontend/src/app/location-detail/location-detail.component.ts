import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import {Geo58Service} from '../services/geo58.service';
import * as opening_hours from 'opening_hours';
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
  @Input() draggedUp = false;
  @Output() goUp = new EventEmitter<string>();
  @Output() goDown = new EventEmitter<string>();

  permalink = '';
  osmlink = '';
  locationType = '';
  locationSubType = '';
  labels: object = {};
  opening_hours = '';
  open_now = undefined;

  constructor(
    private geo58service: Geo58Service
  ) {
  }

  ngOnInit() {
    this.parseFeatures();
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.parseFeatures();
  }

  private parseFeatures() {
    if (!this.feature) {
      return;
    }
    this.locationType = this.feature.values_.locationType;
    this.locationSubType = this.feature.values_.locationSubType;
    this.labels = this.feature.values_.labels;
    const lonLat = toLonLat(this.feature.getGeometry().getCoordinates());
    this.permalink = this.getPermalink(lonLat);
    this.osmlink = this.getOsmLink();
    this.parseOpeningHours();
  }

  private getPermalink(lonLat: object) {
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

  private getOsmLink() {
    if (!this.labels || !this.labels['osm_data_type'] || !this.labels['osm_id']) {
      return '';
    }

    return 'https://www.openstreetmap.org/edit?editor=id&' + this.labels['osm_data_type'] + '=' + this.labels['osm_id'];
  }

  private getShortLink(propertyUrlPart, lonLat) {
    this.geo58service.toGeo58(19, lonLat[1], lonLat[0])
      .subscribe(hashUrl => {
          this.permalink = environment.shortLinkBaseUrl + '/' + hashUrl['geo58'] + ';' + propertyUrlPart;
        },
        error => {
          console.error('Error: Geo58 link could net be retrieved');
          console.error(error);
        });
  }

  private parseOpeningHours() {
    this.opening_hours = '';
    this.open_now = undefined;
    if (!this.feature.values_.labels['opening_hours']) {
      return '';
    }

    const oh = new opening_hours(this.feature.values_.labels['opening_hours'], null);
    // TODO: pass nominatim object instead of null, or set default location to Austria or the viewport
    this.opening_hours = this.feature.values_.labels['opening_hours'];
    this.open_now = oh.getState();
  }

  public emitGoUp() {
    console.log('goUp');
    this.goUp.emit('goUp');
  }

  public emitGoDown() {
    console.log('goDown');
    this.goDown.emit('goDown');
  }
}
