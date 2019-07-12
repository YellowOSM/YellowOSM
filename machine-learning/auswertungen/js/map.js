import jQuery from 'jquery/dist/jquery.js';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import {Heatmap as HeatmapLayer, Tile as TileLayer} from 'ol/layer.js';
import OlXYZ from 'ol/source/XYZ';
import VectorSource from 'ol/source/Vector.js';
import GeoJSON from "ol/format/GeoJSON";
import {fromLonLat, toLonLat} from 'ol/proj';


jQuery(document).ready(function ($) {
    let vector = new HeatmapLayer({
        source: new VectorSource({
            url: 'data/graz-restaurants.json',
            format: new GeoJSON({
                extractStyles: false
            })
        }),
        blur: 5,
        radius: 15
    });

    vector.getSource().on('addfeature', function (event) {
        event.feature.set('weight', 2);
    });

    let raster = new TileLayer({
        source: new OlXYZ({
            url: '//maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
        })
    });

    let map = new Map({
        layers: [raster, vector],
        target: 'map',
        view: new View({
            center: fromLonLat([15.4395, 47.0707]),
            zoom: 15
        })
    });
});
