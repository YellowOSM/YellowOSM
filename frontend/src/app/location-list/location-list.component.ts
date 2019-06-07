import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import Feature from 'ol/Feature';
import {AppSettings} from '../app.settings';
import {OpeningHoursService} from '../services/opening-hours.service';

@Component({
  selector: 'app-location-list',
  templateUrl: './location-list.component.html',
  styleUrls: ['./location-list.component.scss']
})
export class LocationListComponent implements OnChanges, OnInit {
  @Input() selectedFeature: Feature = null;
  @Input() features: Feature[] = [];
  @Output() selectFeature = new EventEmitter();

  INITIAL_BOTTOM_OFFSET = 250;
  topStartPos = 0;
  topPos = 0;

  LOAD_OFFSET_PIXEL = 400;
  LOAD_OFFSET_ITEMS = 5;
  scrollFeatures = [];
  itemOffset = 5;
  scrollOffset = this.topPos;

  scrolling = false;

  constructor(
    private opening_hours_service: OpeningHoursService
  ) {
  }

  ngOnInit() {
    if (window.innerWidth >= AppSettings.BREAKPOINT_DESKTOP) {
      this.topPos = AppSettings.MIN_TOP_OFFSET;
    } else {
      this.topPos = window.innerHeight - this.INITIAL_BOTTOM_OFFSET;
    }
  }

  public getOpenNow(hours_string) {
    return this.opening_hours_service.getOpenNow(hours_string);
  }

  public getClasses() {
    return this.scrolling ? 'location__list scrolling' : 'location__list';
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
    if (event.deltaY < 0 && this.topPos < (window.innerHeight - this.features.length * (this.LOAD_OFFSET_PIXEL / this.LOAD_OFFSET_ITEMS))) {
      return;
    }

    this.topPos = Math.min(window.innerHeight - AppSettings.MIN_BOTTOM_OFFSET, this.topStartPos + event.deltaY);
    if (this.topPos < (this.scrollOffset - this.LOAD_OFFSET_PIXEL)) {
      this.appendScrollFeatures();
      this.scrollOffset -= this.LOAD_OFFSET_PIXEL;
    }
  }

  emitSelectFeature(feature) {
    this.selectFeature.emit({event: feature});
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.features && this.features.length > 0) {
      this.scrollFeatures = this.features.slice(0, this.LOAD_OFFSET_ITEMS);
      this.scrollFeatures.forEach((feature) => {
        feature.open_now = this.getOpenNow(feature.values_.labels['opening_hours']);
      });
      this.itemOffset = this.LOAD_OFFSET_ITEMS;
    }
  }

  private appendScrollFeatures() {
    this.itemOffset += this.LOAD_OFFSET_ITEMS;
    const newFeatures = this.features.slice(this.itemOffset, this.itemOffset + this.LOAD_OFFSET_ITEMS);
    newFeatures.forEach((feature) => {
      feature.open_now = this.getOpenNow(feature.values_.labels['opening_hours']);
    });
    this.scrollFeatures = this.scrollFeatures.concat(newFeatures);
  }
}
