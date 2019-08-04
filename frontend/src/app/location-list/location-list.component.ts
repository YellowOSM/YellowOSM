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
  @Input() hidePanels;
  @Output() selectFeature = new EventEmitter();

  INITIAL_BOTTOM_OFFSET = 250;
  topStartPos = 0;
  topPos = 0;

  DETAIL_ELEMENT_HEIGHT = 105; // height of .location__list-detail + margin (30px)
  LOAD_OFFSET_ITEMS = 15;
  scrollFeatures = [];
  itemOffset = this.LOAD_OFFSET_ITEMS;
  scrolling = false;

  constructor(
    private opening_hours_service: OpeningHoursService
  ) {
  }

  ngOnInit() {
    this.resetPanelStatus();
  }

  public resetPanelStatus() {
    if (window.innerWidth >= AppSettings.BREAKPOINT_DESKTOP) {
      this.topPos = AppSettings.MIN_TOP_OFFSET;
    } else {
      this.topPos = window.innerHeight - this.INITIAL_BOTTOM_OFFSET;
    }
    this.itemOffset = this.LOAD_OFFSET_ITEMS;
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.features && changes.features.currentValue.length == 0) {
      this.resetPanelStatus();
    }
    if (this.features && this.features.length > 0) {
      this.itemOffset = this.LOAD_OFFSET_ITEMS;
      this.scrollFeatures = this.features.slice(0, this.LOAD_OFFSET_ITEMS);
      this.scrollFeatures.forEach((feature) => {
        feature.open_now = this.getOpenNow(feature.values_.labels['opening_hours']);
      });
      this.itemOffset = this.LOAD_OFFSET_ITEMS;
    }
  }

  public getOpenNow(hours_string) {
    return this.opening_hours_service.getOpenNow(hours_string);
  }

  public getClasses() {
    let className = 'location__list';
    if (!this.hidePanels && this.features && this.features.length > 0) {
      if (this.scrolling) {
        className += ' scrolling';
      }
      if (this.selectedFeature && window.innerWidth < AppSettings.BREAKPOINT_DESKTOP) {
        className += ' hidden';
      }
    } else {
      className += ' hidden';
    }
    return className;
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
    if (event.deltaY < 0 && this.topPos < (window.innerHeight - this.features.length * this.DETAIL_ELEMENT_HEIGHT  - 15)) {
      return;
    }

    this.topPos = Math.min(window.innerHeight - AppSettings.MIN_BOTTOM_OFFSET, this.topStartPos + event.deltaY);
    if (event.deltaY < 0 && this.topPos < (window.innerHeight - this.scrollFeatures.length * this.DETAIL_ELEMENT_HEIGHT)) {
      this.appendScrollFeatures();
    }
  }

  onPanToParent(event: any): void {
    // propagate pan event to list container
    this.onPan(event);
  }

  emitSelectFeature(feature) {
    this.selectFeature.emit({event: feature});
  }

  private appendScrollFeatures() {
    if (this.scrollFeatures.length >= this.features.length) {
      return;
    }
    const newFeatures = this.features.slice(this.itemOffset, this.itemOffset + this.LOAD_OFFSET_ITEMS);
    this.itemOffset += this.LOAD_OFFSET_ITEMS;
    newFeatures.forEach((feature) => {
      feature.open_now = this.getOpenNow(feature.values_.labels['opening_hours']);
    });
    this.scrollFeatures = this.scrollFeatures.concat(newFeatures);
  }

  onScroll($event) {
    if (($event.target.scrollTop + window.innerHeight) > (this.scrollFeatures.length * this.DETAIL_ELEMENT_HEIGHT)) {
      this.appendScrollFeatures();
    }
  }
}
