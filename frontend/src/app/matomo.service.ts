import {Injectable} from '@angular/core';
import {MatomoTracker} from 'ngx-matomo';

@Injectable({
  providedIn: 'root'
})
export class MatomoService {

  constructor(
    private matomoTracker: MatomoTracker
  ) {
  }

  trackPageView(title) {
    this.matomoTracker.trackPageView(title);
  }

  trackPoiOpenFromMap(clickedFeature) {
    this.matomoTracker.trackEvent(
      'poi',
      'open-from-map',
      clickedFeature.values_.hasOwnProperty('type') ? clickedFeature['type'] : 'none');
  }

  trackPoiOpenFromList(clickedFeature) {
    this.matomoTracker.trackEvent(
      'poi',
      'open-from-list',
      clickedFeature.values_.hasOwnProperty('type') ? clickedFeature['type'] : 'none');
  }

  trackSearch(query) {
    this.matomoTracker.trackSiteSearch(query);
  }

  trackPoiAction(actionType: string) {
    this.matomoTracker.trackEvent(
      'poi',
      'action',
      actionType
    )
  }

  trackGeoLocation() {
    this.matomoTracker.trackEvent(
      'map',
      'getGeoLocation'
    )
  }
}
