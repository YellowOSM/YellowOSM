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

  @Input() selectedFeature: Feature = null;
  @Input() @Output() features: Feature[] = [];
  @Input() draggedUp = false;
  @Input() showFeatureList = false;
  @Output() goUp = new EventEmitter<string>();
  @Output() goDown = new EventEmitter<string>();
  @Output() closeFeature = new EventEmitter<string>();
  @Output() closeFeatureList = new EventEmitter<string>();

  permalink = '';
  osmlink = '';
  locationType = '';
  locationSubType = '';
  labels: object = {};
  opening_hours = '';
  open_now = undefined;
  open_next = undefined;

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
    if (!this.selectedFeature) {
      return;
    }
    this.locationType = this.selectedFeature.values_.locationType;
    this.locationSubType = this.selectedFeature.values_.locationSubType;
    this.labels = this.selectedFeature.values_.labels;
    const lonLat = toLonLat(this.selectedFeature.getGeometry().getCoordinates());
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
    if (!this.selectedFeature.values_.labels['opening_hours']) {
      return '';
    }

    const oh = new opening_hours(this.selectedFeature.values_.labels['opening_hours'], null);
    // TODO: pass nominatim object instead of null, or set default location to Austria or the viewport
    this.opening_hours = this.selectedFeature.values_.labels['opening_hours'];
    this.open_now = oh.getState();
    const days = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];

    this.open_next = oh.getNextChange();
    this.open_next = days[this.open_next.getDay()] + ', ' + this.addZero(this.open_next.getHours()) + ':' +
      this.addZero(this.open_next.getMinutes());
  }

  private addZero(i) {
    if (i < 10) {
      i = '0' + i;
    }
    return i;
  }

  public emitGoUp() {
    this.goUp.emit('goUp');
  }

  public emitGoDown() {
    this.goDown.emit('goDown');
  }

  public emitCloseFeature() {
    this.closeFeature.emit('closeFeature');
  }

  public emitCloseFeatureList() {
    this.closeFeatureList.emit('closeFeatureList');
  }
}
