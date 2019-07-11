import {Injectable} from '@angular/core';
import * as opening_hours from 'opening_hours';

@Injectable({
  providedIn: 'root'
})
export class OpeningHoursService {

  DAYS = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];

  constructor() {
  }

  getOpenNow(hours_string: string) {
    if (!hours_string) {
      return false;
    }
    const oh = new opening_hours(hours_string, null, {'locale': 'de'});
    // TODO: pass nominatim object instead of null, or set default location to Austria or the viewport
    return oh.getState();
  }

  getOpenNowAndNext(hours_string: string) {
    if (!hours_string) {
      return {
        open_now: undefined,
        open_next: undefined
      };
    }
    const oh = new opening_hours(hours_string, null);
    // TODO: pass nominatim object instead of null, or set default location to Austria or the viewport

    const open_next = oh.getNextChange();
    const open_next_text = this.DAYS[open_next.getDay()] + ', ' + this.addZero(open_next.getHours()) + ':' +
      this.addZero(open_next.getMinutes());

    return {
      open_now: oh.getState(),
      open_next: open_next_text,
      open_pretty: oh.prettifyValue({
        conf: {
          locale: 'de',
          rule_sep_string: '<br>',
          print_semicolon: false,
          zero_pad_month_and_week_numbers: false,
          zero_pad_hour: false,
          one_zero_if_hour_zero: true
        }
      }).replace(' off', ' geschlossen')
        .replace(' closed', ' geschlossen')
        .replace('PH', 'Feiertag')
        .replace(',', ', ')
    };
  }

  private addZero(i) {
    if (i < 10) {
      i = '0' + i;
    }
    return i;
  }
}
