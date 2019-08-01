import {Component, OnInit} from '@angular/core';
import {MatomoInjector} from 'ngx-matomo';
import {environment} from '../environments/environment';
import {SwUpdate} from '@angular/service-worker';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'frontend';

  constructor(
    private matomoInjector: MatomoInjector,
    private swUpdate: SwUpdate
  ) {
  }

  ngOnInit() {
    this.matomoInjector.init(environment.matomoBaseUrl, environment.matomoWebsiteId);
    this.swUpdate.available.subscribe(event => {
      console.log('A newer version is now available. Refresh the page now to update the cache');
    });
    console.log('checking for SW update...');
    this.swUpdate.checkForUpdate();
  }
}
