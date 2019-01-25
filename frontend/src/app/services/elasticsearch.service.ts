import {Injectable} from '@angular/core';
import * as elasticsearch from 'elasticsearch-browser';
import {Client} from 'elasticsearch-browser';
import {environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ElasticsearchService {

  private client: Client;

  constructor() {
    if (!this.client) {
      this._connect();
    }
  }

  private _connect() {
    this.client = new elasticsearch.Client({
      host: environment.elasticSearchBaseUrl,
    });
  }

  isAvailable(): any {
    return this.client.ping({
      requestTimeout: Infinity,
      body: 'hello yosm!'
    });
  }

  fullTextSearch(userQuery: string): any {
    return this.client.search({
      index: 'yosm',
      type: '_doc',
      filterPath: ['hits.hits._source', 'hits.total', '_scroll_id'],
      body: {
        'query': {
          'bool': {
            'must': {
              'query_string': {
                'query': userQuery + '*'
              }
            },
            'filter': {
              'geo_bounding_box': {
                'location': {
                  'top_left': {
                    'lat': 48,
                    'lon': 10
                  },
                  'bottom_right': {
                    'lat': 40,
                    'lon': 16
                  }
                }
              }
            }
          }
        }
      }
    });
  }
}
