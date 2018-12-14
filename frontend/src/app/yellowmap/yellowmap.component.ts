import {Component, OnInit} from '@angular/core';

import OlMap from 'ol/Map';
import OlXYZ from 'ol/source/XYZ';
import OlTileLayer from 'ol/layer/Tile';
import OlView from 'ol/View';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import {Vector as VectorLayer} from 'ol/layer';
import VectorSource from 'ol/source/Vector';
import {fromLonLat} from 'ol/proj';
import {Circle as CircleStyle, Fill, Icon, Stroke, Style} from 'ol/style';

@Component({
  selector: 'app-yellowmap',
  templateUrl: './yellowmap.component.html',
  styleUrls: ['./yellowmap.component.scss']
})
export class YellowmapComponent implements OnInit {
  map: OlMap;
  source: OlXYZ;
  layer: OlTileLayer;
  view: OlView;

  constructor() {
  }

  ngOnInit() {
    this.source = new OlXYZ({
      url: 'http://tile.osm.org/{z}/{x}/{y}.png'
    });

    this.layer = new OlTileLayer({
      source: this.source
    });

    this.view = new OlView({
      center: fromLonLat([15.4395, 47.0707]),
      zoom: 16
    });

    const styles = {
      'icon': new Style({
        image: new CircleStyle({
          radius: 7,
          fill: new Fill({color: 'red'}),
          stroke: new Stroke({
            color: 'white', width: 2
          })
        })
      })
    };

    const startMarker = new Feature({
      type: 'icon',
      geometry: new Point(fromLonLat([15.4395, 47.0707]))
    });

    const vectorLayer = new VectorLayer({
      source: new VectorSource({
        features: [startMarker]
      }),
      style: function (feature) {
        return styles[feature.get('type')];
      }
    });

    this.map = new OlMap({
      target: 'map',
      layers: [this.layer, vectorLayer],
      view: this.view
    });
  }
}
