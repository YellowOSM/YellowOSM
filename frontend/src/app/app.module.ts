import {BrowserModule, HAMMER_GESTURE_CONFIG, HammerGestureConfig} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {YellowmapComponent} from './yellowmap/yellowmap.component';
import {LocationDetailComponent} from './location-detail/location-detail.component';
import {AboutComponent} from './about/about.component';
import {PageNotFoundComponent} from './page-not-found/page-not-found.component';
import {Geo58RedirectComponent} from './geo58-redirect/geo58-redirect.component';
import {HttpClientModule} from '@angular/common/http';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MaterialModule} from './material.module';
import * as Hammer from 'hammerjs';
import {LocationListComponent} from './location-list/location-list.component';
import { ServiceWorkerModule } from '@angular/service-worker';
import { environment } from '../environments/environment';

export class MyHammerConfig extends HammerGestureConfig {
  overrides = <any>{
    pan: {direction: Hammer.DIRECTION_VERTICAL}
  };
}

@NgModule({
  declarations: [
    AppComponent,
    YellowmapComponent,
    LocationDetailComponent,
    LocationListComponent,
    AboutComponent,
    PageNotFoundComponent,
    Geo58RedirectComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MaterialModule,
    ReactiveFormsModule,
    ServiceWorkerModule.register('ngsw-worker.js', { enabled: environment.production }),
  ],
  providers: [
    {
      provide: HAMMER_GESTURE_CONFIG,
      useClass: MyHammerConfig
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
