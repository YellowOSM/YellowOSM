import {ChangeDetectorRef, Component, OnInit} from '@angular/core';

import OlMap from 'ol/Map';
import OlXYZ from 'ol/source/XYZ';
import OlTileLayer from 'ol/layer/Tile';
import OlView from 'ol/View';
import {Vector as VectorLayer} from 'ol/layer';
import VectorSource from 'ol/source/Vector';
import {GeoJSON} from 'ol/format';
import {fromLonLat, transformExtent} from 'ol/proj';
import {Circle as CircleStyle, Fill, Icon, Stroke, Style} from 'ol/style';
import {bbox as bboxStrategy} from 'ol/loadingstrategy.js';
import {ElasticsearchService} from '../services/elasticsearch.service';
import Point from 'ol/geom/Point';
import Feature from 'ol/Feature';

@Component({
  selector: 'app-yellowmap',
  templateUrl: './yellowmap.component.html',
  styleUrls: ['./yellowmap.component.scss']
})
export class YellowmapComponent implements OnInit {
  map: OlMap;
  source: OlXYZ;
  layer: OlTileLayer;
  esLayer: VectorLayer;
  view: OlView;
  userQuery = '';
  esIsConnected = false;
  esStatus: string;
  esSearchResult = [];
  esSource: VectorSource;
  selection = {};
  selectionDetails = '';

  constructor(private es: ElasticsearchService, private cd: ChangeDetectorRef) {
    this.esIsConnected = false;
  }

  ngOnInit() {
    this.initElasticsearch();
    this.searchElasticSearch();

    this.source = new OlXYZ({
      url: '//tile-b.openstreetmap.fr/hot/{z}/{x}/{y}.png'
    });

    this.layer = new OlTileLayer({
      source: this.source
    });

    this.view = new OlView({
      center: fromLonLat([15.4395, 47.0707]),
      zoom: 16
    });

    const that = this;

    this.esSource = new VectorSource({
      format: new GeoJSON(),
      loader: function (extent, resolution, projection) {
        that.esSearchResult.forEach(result => {
          const featurething = new Feature({
            name: result['_source']['name'],
            geometry: new Point(fromLonLat([result['_source']['location'][0], result['_source']['location'][1]]))
          });
          featurething.on('click', function (args) {
            console.log('click');
            console.log(featurething);
          });
          that.esSource.addFeature(featurething);
        });
      },
      strategy: bboxStrategy
    });

    this.esLayer = new VectorLayer({
      source: this.esSource,
      style: function(feature) {
        let color = 'rgba(255, 211, 3, 0.7)';
        if (that.selection.hasOwnProperty('ol_uid') && that.selection.ol_uid === feature.ol_uid) {
          color = 'rgba(200,20,20,0.8)';
        }
        return new Style({
          image: new CircleStyle({
            radius: 7,
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

    this.map = new OlMap({
      target: 'map',
      layers: [
        this.layer,
        this.esLayer
      ],
      view: this.view
    });

    this.map.on('click', function (event) {
      const features = that.map.getFeaturesAtPixel(event.pixel);
      if (!features) {
        that.selection = {};
        that.selectionDetails = '';
        return;
      }
      that.selection = features[0];

      that.selectionDetails = features[0].values_['name'];
      // force redraw
      that.esLayer.setStyle(that.esLayer.getStyle());
    });
  }

  search() {
    console.log('TODO: trigger map refresh');
  }

  private initElasticsearch() {
    this.es.isAvailable().then(() => {
      this.esStatus = 'OK';
      this.esIsConnected = true;
    }, error => {
      this.esStatus = 'Fehler beim Verbinden';
      this.esIsConnected = false;
      console.error('Server is down', error);
    }).then(() => {
      this.cd.detectChanges();
    });
  }

  private searchElasticSearch() {
    this.es.fullTextSearch().then((result) => {
      this.esStatus = 'OK';
      console.log(result);
      if (result !== null && result.hits.total > 0) {
        this.esSearchResult = result['hits']['hits'];
        this.esLayer.getSource().clear();
        this.esLayer.getSource().refresh();
      } else {
        this.esSearchResult = [];
      }
    }, error => {
      this.esStatus = 'Fehler in der Suche';
      this.esSearchResult = [];
      console.error('Server is down', error);
    }).then(() => {
      this.cd.detectChanges();
    });
  }
}
