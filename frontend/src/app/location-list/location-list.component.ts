import {Component, EventEmitter, Input, Output} from '@angular/core';
import Feature from 'ol/Feature';
import {AppSettings} from '../app.settings';
import {OpeningHoursService} from '../services/opening-hours.service';

@Component({
  selector: 'app-location-list',
  templateUrl: './location-list.component.html',
  styleUrls: ['./location-list.component.scss']
})
export class LocationListComponent {
  @Input() selectedFeature: Feature = null;
  @Input() features: Feature[] = [];
  @Output() selectFeature = new EventEmitter();

  INITIAL_BOTTOM_OFFSET = 250;
  topStartPos = 0;
  topPos = window.innerHeight - this.INITIAL_BOTTOM_OFFSET;

  constructor(
    private opening_hours_service: OpeningHoursService
  ) {
  }

  public getOpenNow(hours_string) {
    return this.opening_hours_service.getOpenNow(hours_string);
  }

  onPanStart(event: any): void {
    this.topStartPos = this.topPos;
  }

  onPan(event: any): void {
    if (window.innerWidth >= AppSettings.BREAKPOINT_DESKTOP) {
      return;
    }

    event.preventDefault();
    this.topPos = Math.max(AppSettings.MIN_BOTTOM_OFFSET, this.topStartPos + event.deltaY);
    this.topPos = Math.min(window.innerHeight - AppSettings.MIN_BOTTOM_OFFSET, this.topPos);
  }

  emitSelectFeature(feature) {
    this.selectFeature.emit({event: feature});
  }
}
