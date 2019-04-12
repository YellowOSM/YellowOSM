import {Injectable} from '@angular/core';
import * as elasticsearch from 'elasticsearch-browser';
import {Client} from 'elasticsearch-browser';
import {environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ElasticsearchService {

  constructor() {
    if (!this.client) {
      this._connect();
    }
  }

  private client: Client;

  private static getCommonFullTextQueryBody(userQuery: string) {
    return {
      index: environment.elasticSearchIndex,
      type: '_doc',
      filterPath: ['hits.hits._source', 'hits.total', '_scroll_id'],
      body: {
        'size': 300,
        'query': {
          'bool': {
            'should': [
              {
                'query_string':
                  {
                    'query': userQuery.trim() + '*',
                    'default_operator': 'AND',
                    'fields': [
                      'labels.name^5',
                      'description^2',
                      // 'labels.website^3',
                      // 'labels.contact_website',
                      // 'labels.addr_street',
                      'labels.addr_city',
                      'labels.amenity',
                      'labels.tourism',
                      'labels.sport',
                      'labels.craft',
                      'labels.leisure',
                      'labels.shop',
                      'labels.healthcare',
                      'labels.emergency',
                      'labels.healthcare_speciality'
                    ]
                  }
              }
            ],
            'minimum_should_match': 1,
          }
        }
      }
    };
  }

  private _connect() {
    this.client = new elasticsearch.Client({
      host: environment.elasticSearchBaseUrl,
    });
  }

  public isAvailable(): any {
    return this.client.ping({
      requestTimeout: Infinity,
      body: 'hello yosm!'
    });
  }

  public fullTextBoundingBoxSearch(userQuery: string, topLeft: any, bottomRight: any) {
    const esQuery = ElasticsearchService.getCommonFullTextQueryBody(userQuery);
    esQuery.body.query.bool['filter'] = {
      'geo_bounding_box': {
        'location': {
          'top_left': {
            'lat': topLeft[1],
            'lon': topLeft[0]
          },
          'bottom_right': {
            'lat': bottomRight[1],
            'lon': bottomRight[0]
          }
        }
      }
    };

    return this.client.search(esQuery);
  }

  public fullTextClosestSearch(userQuery: string, center: any) {
    const esQuery = ElasticsearchService.getCommonFullTextQueryBody(userQuery);
    esQuery.body.size = 1;
    esQuery.body['sort'] = [
      {
        '_geo_distance': {
          'location': {
            'lat': center[1],
            'lon': center[0]
          },
          'order': 'asc',
          'unit': 'km',
          'distance_type': 'plane'
        }
      }
    ];
    return this.client.search(esQuery);
  }

  public searchByOsmId(osmId: string): any {
    return this.client.search({
      index: environment.elasticSearchIndex,
      type: '_doc',
      filterPath: ['hits.hits._source', 'hits.total', '_scroll_id'],
      body: {
        'query': {
          'match': {
            'osm_id': osmId
          },
        }
      }
    });
  }

  public searchVicinityByProperty(propertyType: string, propertyValue: string, center: any): any {
    const propertyTypeString = 'labels.' + propertyType;
    return this.client.search({
      index: environment.elasticSearchIndex,
      type: '_doc',
      filterPath: ['hits.hits._source', 'hits.total', '_scroll_id'],
      body: {
        'size': 4,
        'query': {
          'bool': {
            'must': [
              {'match': {[propertyTypeString]: propertyValue}}
            ],
            'filter': [{
              'geo_distance': {
                'distance': '10m',
                'location': {
                  'lat': center[1],
                  'lon': center[0]
                }
              }
            }]
          }
        },
        'sort': [
          {
            '_geo_distance': {
              'location': {
                'lat': center[1],
                'lon': center[0]
              },
              'order': 'asc',
              'unit': 'km',
              'distance_type': 'plane'
            }
          }
        ]
      }
    });
  }
}
