export const environment = {
  production: true,
  localDevEnv: false,
  name: 'test',
  elasticSearchBaseUrl: 'https://es.yosm.at',
  elasticSearchIndex: 'yosm_dev',
  // Wikimedia
  tileServerURLs: [
    {'label': 'Wikimedia', 'url': '//maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', 'attribution': '<a href="https://foundation.wikimedia.org/wiki/Maps_Terms_of_Use" target="_blank">CC-BY 4.0 Wikimedia</a> - <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'},
    {'label': 'HOT - Humanitarian map style', 'url': '//a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', 'attribution': '<a href="https://github.com/hotosm/HDM-CartoCSS" target="_blank">HOT CC0</a> - <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'},
    // {'label': 'HikeBikeMap', 'url': '//tiles.wmflabs.org/hikebike/${z}/${x}/${y}.png', 'attribution': 'Map tiles by Carto, under CC BY 3.0. Data by <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>, under ODbL.'},
    // {'label': 'ÖPNV-Karte', 'url': '//tile.memomaps.de/tilegen/${z}/${x}/${y}.png', 'attribution': 'Map <a href="https://memomaps.de/" target="_blank">memomaps.de</a> CC-BY-SA, map data <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> ODbL'},
  ],
  apiBaseUrl: 'https://dev.yosm.at/api',
  shortLinkBaseUrl: 'https://dev.yosm.at/s',
  matomoBaseUrl: '//matomo.yosm.at/',
  matomoWebsiteId: 2,
  gitCommitHash: '%YOSM-COMMIT%',
  max_search_results: 300
};
