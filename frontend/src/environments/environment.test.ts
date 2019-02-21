export const environment = {
  production: false,
  name: 'test',
  elasticSearchBaseUrl: 'https://es.yosm.at',
  elasticSearchIndex: 'yosm',
  // no label standard tile:
  // tileServerURL: '//tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png',
  // bergfex (not sure if ok to use)
  // tileServerURL: '//maps.bergfex.at/osm/512px/{z}/{x}/{y}.jpg',
  // HOT:
  tileServerURL: '//a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
  // Stamen:
  // tileServerURL: '//a.tile.stamen.com/toner/{z}/{x}/{y}.png',
  apiBaseUrl: 'https://dev.yosm.at/api',
  shortLinkBaseUrl: 'https://dev.yosm.at/s'
};
