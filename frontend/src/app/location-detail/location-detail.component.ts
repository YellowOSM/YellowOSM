import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import {Geo58Service} from '../services/geo58.service';
import * as opening_hours from 'opening_hours';
import {environment} from '../../environments/environment';
import Feature from 'ol/Feature';
import {toLonLat} from 'ol/proj';
import {AppSettings} from '../app.settings';
import {OpeningHoursService} from '../services/opening-hours.service';
import {MatomoService} from '../matomo.service';

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
  @Input() hidePanels;
  @Output() closeFeature = new EventEmitter<string>();

  BOTTOM_OFFSET = 100;
  INITIAL_BOTTOM_OFFSET = 400;
  topStartPos = 0;
  topPos = window.innerHeight - this.INITIAL_BOTTOM_OFFSET;

  permalink = '';
  osmlink = '';
  locationType = '';
  locationSubType = '';
  labels: object = {};
  latLonStr = '';
  opening_hours = '';
  open_now = undefined;
  open_next = undefined;
  opening_hours_pretty = undefined;

  constructor(
    private geo58service: Geo58Service,
    private opening_hours_service: OpeningHoursService,
    private matomoService: MatomoService
  ) {
  }

  ngOnInit() {
    if (window.innerWidth >= AppSettings.BREAKPOINT_DESKTOP) {
      this.topPos = AppSettings.MIN_TOP_OFFSET;
    } else {
      this.topPos = window.innerHeight - this.INITIAL_BOTTOM_OFFSET;
    }
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
    this.latLonStr = lonLat[1] + '%2C' + lonLat[0];
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
    const hours = this.opening_hours_service.getOpenNowAndNext(this.selectedFeature.values_.labels['opening_hours'], this.selectedFeature.values_.labels['addr_country']);
    this.open_now = hours['open_now'];
    this.open_next = hours['open_next'];
    this.opening_hours_pretty = hours['open_pretty'];
    this.opening_hours = this.selectedFeature.values_.labels['opening_hours'];
  }

  public emitCloseFeature() {
    this.closeFeature.emit('closeFeature');
    if (window.innerWidth >= AppSettings.BREAKPOINT_DESKTOP) {
      return;
    }

    this.topPos = window.innerHeight - this.INITIAL_BOTTOM_OFFSET;
  }

  onPanStart(event: any): void {
    if (window.innerWidth >= AppSettings.BREAKPOINT_DESKTOP) {
      return;
    }

    this.topStartPos = this.topPos;
  }

  onPan(event: any): void {
    if (window.innerWidth >= AppSettings.BREAKPOINT_DESKTOP) {
      return;
    }

    event.preventDefault();
    if (event.deltaY < 0 && this.topPos <= AppSettings.MIN_TOP_OFFSET) {
      return;
    }
    
    this.topPos = Math.max(this.BOTTOM_OFFSET, this.topStartPos + event.deltaY);
    this.topPos = Math.min(window.innerHeight - AppSettings.MIN_BOTTOM_OFFSET, this.topStartPos + event.deltaY);
  }

  trackPoiAction(actionType: string) {
    this.matomoService.trackPoiAction(actionType);
  }

  getClasses() {
    let className = 'location__detail';
    if (!this.hidePanels && this.selectedFeature) {
      className += ' visible';
    } else {
      className += ' hidden';
    }
    return className;
  }
}
