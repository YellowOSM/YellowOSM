// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
  production: false,
  elasticSearchBaseUrl: 'https://es.yosm.at',
  elasticSearchIndex: 'yosm_dev',
  // no label standard tile:
  // tileServerURL: '//tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png',
  // bergfex (not sure if ok to use)
  // tileServerURL: '//maps.bergfex.at/osm/512px/{z}/{x}/{y}.jpg',
  // HOT:
  // tileServerURL: '//a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
  // Stamen no SSL:
  // tileServerURL: '//a.tile.stamen.com/toner/{z}/{x}/{y}.png',
  // osm.de:
  tileServerURL: '//d.tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png',
  apiBaseUrl: 'https://dev.yosm.at/api'
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.
