import {ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {FormControl} from '@angular/forms';
import {environment} from '../../environments/environment';

import OlMap from 'ol/Map';
import OlXYZ from 'ol/source/XYZ';
import OlTileLayer from 'ol/layer/Tile';
import OlView from 'ol/View';
import Geolocation from 'ol/Geolocation.js';
import {Vector as VectorLayer} from 'ol/layer';
import VectorSource from 'ol/source/Vector';
import {GeoJSON} from 'ol/format';
import {fromLonLat, toLonLat} from 'ol/proj';
import LineString from 'ol/geom/LineString';
import {getBottomRight, getTopLeft} from 'ol/extent';
import {Circle as CircleStyle, Fill, Stroke, Style} from 'ol/style';
import {bbox as bboxStrategy} from 'ol/loadingstrategy.js';
import Point from 'ol/geom/Point';
import Feature from 'ol/Feature';

import * as opening_hours from 'opening_hours';

import {ElasticsearchService} from '../services/elasticsearch.service';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import {LocationDetailComponent} from '../location-detail/location-detail.component';
import {MatAutocompleteTrigger, MatSnackBar} from '@angular/material';
import {AppSettings} from '../app.settings';
import {$e} from 'codelyzer/angular/styles/chars';

@Component({
  selector: 'app-yellowmap',
  templateUrl: './yellowmap.component.html',
  styleUrls: ['./yellowmap.component.scss']
})
export class YellowmapComponent implements OnInit {
  DEBUG = Boolean(false && environment.localDevEnv);
  features = [];
  selectedFeature: Feature = null;
  searchFormControl = new FormControl();
  filteredOptions: Observable<string[]>;
  options: string[] = ['Restaurant', 'Bankomat', 'Apotheke', 'Supermarkt', 'Bar', 'Friseur', 'Pub', 'Cafe', 'Bäckerei'];
  map: OlMap;
  source: OlXYZ;
  esLayer: VectorLayer;
  view: OlView;
  esSearchResult = [];
  esSource: VectorSource;
  geoLocation: Geolocation;
  geoLocationLoading = false;
  @ViewChild('searchInput', { read: MatAutocompleteTrigger, static: true })
  autocomplete: MatAutocompleteTrigger;
  @ViewChild('searchInput', { static: true })
  searchInput: ElementRef;
  @ViewChild('mapElement', { static: true })
  mapElement: ElementRef;
  @ViewChild('toolbarElement', { read: ElementRef, static: true })
  toolbarElement: ElementRef;

  previousUrlParams = {
    zoom: +this.route.snapshot.paramMap.get('zoom'),
    lat: +this.route.snapshot.paramMap.get('lat'),
    lon: +this.route.snapshot.paramMap.get('lon')
  };
  openFirstFeature = false;
  showOnlyOpenedLocations = false;

  constructor(
    private es: ElasticsearchService,
    private cd: ChangeDetectorRef,
    private router: Router,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar
  ) {
  }

  ngOnInit() {
    this.filteredOptions = this.searchFormControl.valueChanges.pipe(
      startWith(''),
      map(value => this._filterAutocomplete(value))
    );

    this.source = new OlXYZ({
      url: environment.tileServerURL,
    });

    const layer = new OlTileLayer({
      source: this.source
    });

    this.view = new OlView({
      center: fromLonLat([+this.route.snapshot.paramMap.get('lon'), +this.route.snapshot.paramMap.get('lat')]),
      zoom: +this.route.snapshot.paramMap.get('zoom'),
      maxZoom: 19,
      enableRotation: false
    });

    const that = this;
    this.esSource = new VectorSource({
      format: new GeoJSON(),
      loader: (extent, resolution, projection) => {
        that.features = [];
        that.esSearchResult.forEach(result => {
          if (that.showOnlyOpenedLocations) {
            try {
              const oh = new opening_hours(result['_source']['labels']['opening_hours'], null);
              // TODO: pass nominatim object instead of null, or set default location to Austria or the viewport
              if (!oh.getState()) {
                return;
              }
            } catch (error) {
              return;
            }
          }
          const lonLat = fromLonLat([result['_source']['location'][0], result['_source']['location'][1]]);
          const featurething = new Feature({
            name: result['_source']['name'],
            locationType: result['_source']['type'],
            locationSubType: result['_source']['subtype'],
            geometry: new Point(lonLat),
            labels: result['_source']['labels']
          });
          that.esSource.addFeature(featurething);
          that.features.push(featurething);

          if (featurething.values_.labels && that.selectedFeature && that.selectedFeature.values_.labels &&
            that.selectedFeature.values_.labels.osm_id &&
            featurething.values_.labels.osm_id === that.selectedFeature.values_.labels.osm_id) {
            that.selectedFeature = featurething;
          }
          if ((this.openFirstFeature || this.DEBUG) && !this.selectedFeature) {
            this.selectedFeature = featurething;
            this.openFirstFeature = false;
          }
        });
      },
      strategy: bboxStrategy
    });

    this.esLayer = new VectorLayer({
      source: this.esSource,
      style: (feature) => {
        let color = 'rgba(255, 211, 3, 0.7)';
        if (this.selectedFeature && this.selectedFeature.hasOwnProperty('ol_uid') && this.selectedFeature['ol_uid'] === feature.ol_uid) {
          color = 'rgba(200,20,20,0.8)';
        }
        return new Style({
          image: new CircleStyle({
            radius: 11,
            fill: new Fill({
              color: color
            }),
            stroke: new Stroke({
              color: 'rgba(0,0,0,1)', width: 2.5
            })
          })
        });
      },
      strategy: bboxStrategy
    });

    this.geoLocation = new Geolocation({
      trackingOptions: {
        enableHighAccuracy: true
      },
      projection: this.view.getProjection()
    });

    // handle geolocation error.
    this.geoLocation.on('error', (error) => {
      console.log('YOSM GEO ERROR');
      console.log(error);
    });

    const accuracyFeature = new Feature();
    this.geoLocation.on('change:accuracyGeometry', () => {
      accuracyFeature.setGeometry(this.geoLocation.getAccuracyGeometry());
    });

    const positionFeature = new Feature();
    positionFeature.setStyle(new Style({
      image: new CircleStyle({
        radius: 6,
        fill: new Fill({
          color: '#3399CC'
        }),
        stroke: new Stroke({
          color: '#fff',
          width: 2
        })
      })
    }));

    this.geoLocation.on('change:position', () => {
      const coordinates = this.geoLocation.getPosition();
      positionFeature.setGeometry(coordinates ?
        new Point(coordinates) : null);
    });

    const geoLayer = new VectorLayer({
      source: new VectorSource({
        features: [accuracyFeature, positionFeature]
      })
    });

    this.map = new OlMap({
      target: 'map',
      layers: [
        layer,
        geoLayer,
        this.esLayer,
      ],
      controls: [],
      view: this.view
    });

    this.map.on('click', (event) => {
      this.searchInput.nativeElement.blur();
      const features = this.map.getFeaturesAtPixel(event.pixel);
      if (features && features[0].values_.hasOwnProperty('labels')) {
        this.selectedFeature = features[0];
        const padding = 50;
        const center = this.map.getView().getCenter();
        const resolution = this.map.getView().getResolution();

        if (window.innerWidth < AppSettings.BREAKPOINT_DESKTOP
          && event.pixel[1] > (window.innerHeight - AppSettings.MIN_BOTTOM_OFFSET)) {
          const distance = AppSettings.MIN_BOTTOM_OFFSET + padding - (window.innerHeight - event.pixel[1]);
          this.map.getView().animate({center: [center[0], center[1] - distance * resolution]});
        } else if (window.innerWidth >= AppSettings.BREAKPOINT_DESKTOP
          && event.pixel[0] < AppSettings.MIN_LEFT_OFFSET) {
          const distance = AppSettings.MIN_LEFT_OFFSET + padding + event.pixel[0];
          this.map.getView().animate({center: [center[0] - distance * resolution, center[1]]});
        }
      } else {
        this.selectedFeature = null;
      }

      // force redraw
      this.esLayer.setStyle(this.esLayer.getStyle());
    });

    this.map.on('moveend', (evt) => {
      this.searchElasticSearch(false, false);
    });

    this.view.on('change:resolution', (evt) => {
      this.searchElasticSearch(false, false);
    });

    this.map.once('moveend', (evt) => {
      this.openNode();
    });

    // DEBUG
    if (this.DEBUG) {
      this.searchFormControl.setValue('tribeka');
      this.searchElasticSearch();
    }

    const urlSearchTerm = this.route.snapshot.paramMap.get('q');
    if (urlSearchTerm) {
      this.searchFormControl.setValue(urlSearchTerm);
      this.searchElasticSearch();
    }
  }

  public updateUrl() {
    const center = toLonLat(this.view.getCenter());
    let zoom = this.view.getZoom();
    let changeUrl = false;

    const zoomDiff = Math.abs(zoom - this.previousUrlParams['zoom']);
    if (zoomDiff > 0.1) {
      this.previousUrlParams['zoom'] = zoom;
      changeUrl = true;
    } else {
      zoom = this.previousUrlParams['zoom'];
    }

    const latDiff = Math.abs(zoom - this.previousUrlParams['lat']);
    if (latDiff > 0.00001) {
      this.previousUrlParams['lat'] = center[1];
      changeUrl = true;
    } else {
      center[1] = this.previousUrlParams['lat'];
    }

    const lonDiff = Math.abs(zoom - this.previousUrlParams['lon']);
    if (lonDiff > 0.00001) {
      this.previousUrlParams['lon'] = center[0];
      changeUrl = true;
    } else {
      center[0] = this.previousUrlParams['lon'];
    }

    if (changeUrl) {
      let query = '';
      if (this.searchFormControl.value) {
        query = ';q=' + this.searchFormControl.value;
      }
      this.router.navigateByUrl(
        '/' +
        Number.parseFloat(zoom).toFixed(2) + '/' +
        Number.parseFloat(center[1]).toFixed(5) + '/' +
        Number.parseFloat(center[0]).toFixed(5) +
        query,
        {
          replaceUrl: true,
        },
      );
    }
  }

  public hideKeyboard() {
    this.searchInput.nativeElement.blur();
  }

  public closeAutocomplete() {
    this.autocomplete.closePanel();
  }

  public searchElasticSearch(clearResults = true, moveToClosestResult = true) {
    if (clearResults) {
      this.clearSearch();
      this.closeAutocomplete();
      this.hideKeyboard();
    }

    if (this.autocomplete.activeOption) {
      this.searchFormControl.setValue(this.autocomplete.activeOption.value);
    }

    this.updateUrl();

    if (!this.searchFormControl.value || this.searchFormControl.value.length < 2) {
      return;
    }
    const extent = this.view.calculateExtent(this.map.getSize());
    const topLeft = toLonLat(getTopLeft(extent));
    const bottomRight = toLonLat(getBottomRight(extent));

    this.es.fullTextBoundingBoxSearch(this.searchFormControl.value, topLeft, bottomRight).then((result) => {
      if (result !== null && result.hits.total > 0) {
        console.log(result['hits']['hits']);
        this.esSearchResult = result['hits']['hits'];
        this.esLayer.getSource().clear();
        this.esLayer.getSource().refresh();
      } else {
        console.log('empty result for search');
        this.esSearchResult = [];
        if (moveToClosestResult) {
          this.findClosestResult();
        }
      }
    }, error => {
      this.clearSearch();
      console.error('Server is down', error);
    }).then(() => {
      this.cd.detectChanges();
    });
  }

  private findClosestResult() {
    const center = toLonLat(this.view.getCenter());
    this.es.fullTextClosestSearch(this.searchFormControl.value, center).then((closestResults) => {
      if (closestResults !== null && closestResults.hits.total > 0) {
        console.log(closestResults['hits']['hits']);
        this.esSearchResult = closestResults['hits']['hits'];
        this.openFirstFeature = true;
        if (this.geoLocation.getTracking()) {
          const targetCoords = fromLonLat(closestResults.hits.hits[0]._source.location);
          const geoLocation = this.geoLocation.getPosition();
          const polygon = new LineString([targetCoords, geoLocation]);
          this.map.getView().fit(polygon, {size: this.map.getSize()});
        } else {
          const coords = fromLonLat(closestResults.hits.hits[0]._source.location);
          this.map.getView().animate({center: coords});
        }
      } else {
        console.log('empty result for closest search');
        this.snackBar.open('keine Ergebnisse gefunden', 'okay', {
          duration: 3000,
          verticalPosition: 'top'
        });
      }
    }, error => {
      this.clearSearch();
      console.error('Server is down', error);
    }).then(() => {
      this.cd.detectChanges();
    });
  }

  private clearSearch() {
    this.esSearchResult = [];
    this.selectedFeature = null;
    this.esLayer.getSource().clear();
    this.esLayer.getSource().refresh();
  }

  public getLocation() {
    this.geoLocation.setTracking(true);
    this.geoLocationLoading = true;
    navigator.geolocation.getCurrentPosition((pos) => {
        const coords = fromLonLat([pos.coords.longitude, pos.coords.latitude]);
        this.map.getView().animate({center: coords, zoom: 17});
        this.geoLocationLoading = false;
      }, (err) => {
        console.warn(`ERROR(${err.code}): ${err.message}`);
        this.geoLocationLoading = false;
      },
      {
        maximumAge: Infinity,
        timeout: 8000
      }
    );
  }

  private getPropertyValueFromUrl() {
    for (let i = 0; i < LocationDetailComponent.PERMALINK_ID_PROPERTIES.length; i++) {
      const param = this.route.snapshot.paramMap.get(LocationDetailComponent.PERMALINK_ID_PROPERTIES[i]);
      if (!param) {
        continue;
      }
      return {
        propertyType: LocationDetailComponent.PERMALINK_ID_PROPERTIES[i],
        propertyValue: param
      };
    }
    return false;
  }

  private openNode() {
    const urlPropertyValue = this.getPropertyValueFromUrl();
    if (!urlPropertyValue) {
      return;
    }

    const center = [
      +this.route.snapshot.paramMap.get('lon'),
      +this.route.snapshot.paramMap.get('lat')
    ];
    const that = this;
    that.es.searchVicinityByProperty(
      urlPropertyValue.propertyType,
      urlPropertyValue.propertyValue,
      center)
      .then((result) => {
        if (result !== null && result.hits.total > 0) {
          const node = result['hits']['hits'][0];
          const featurething = new Feature({
            name: node['_source']['name'],
            labels: node['_source']['labels'],
            geometry: new Point(fromLonLat([node._source.location[0], node._source.location[1]]))
          });
          that.addAndSelectFeature(featurething);
        }
      }, error => {
        console.error('Fehler bei Auflösen von Permalink', error);
      }).then(() => {
      that.cd.detectChanges();
    });
  }

  private addAndSelectFeature(featurething) {
    this.esLayer.getSource().addFeature(featurething);
    this.selectedFeature = featurething;
  }

  private _filterAutocomplete(value: string): string[] {
    const filterValue = value.toLowerCase();

    return this.options.filter(option => option.toLowerCase().indexOf(filterValue) === 0);
  }

  public removeSearchText() {
    this.searchFormControl.setValue('');
    this.clearSearch();
  }

  public closeFeature(event) {
    this.selectedFeature = null;
    // force redraw
    this.esLayer.setStyle(this.esLayer.getStyle());
  }

  public toogleOpenedLocations() {
    this.showOnlyOpenedLocations = !this.showOnlyOpenedLocations;
    this.searchElasticSearch();
  }

  selectFeature($event: any) {
    this.selectedFeature = $event.event;
    this.esLayer.getSource().refresh();
  }
}
