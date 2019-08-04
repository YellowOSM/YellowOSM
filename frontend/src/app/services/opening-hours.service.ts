import {Injectable} from '@angular/core';
import * as opening_hours from 'opening_hours';

@Injectable({
  providedIn: 'root'
})
export class OpeningHoursService {

  DAYS = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
  today = new Date()
  tomorrow = new Date(this.today.getTime() + (24 * 60 * 60 * 1000));

  constructor() {
  }

  getOpenNow(hours_string: string, country_code="at") {
    if (!hours_string) {
      return false;
    }
    const nominatim_object =  {
      "address": {
        "country_code": country_code.toLowerCase()
      }
    };
    const oh = new opening_hours(hours_string, nominatim_object, {'locale': 'de'});
    // TODO: pass correct country code
    return oh.getState();
  }

  getOpenNowAndNext(hours_string: string, country_code="at") {
    if (!hours_string) {
      return {
        open_now: undefined,
        open_next: undefined
      };
    }
    const nominatim_object =  {
      "address": {
        "country_code": country_code.toLowerCase()
      }
    };
    const oh = new opening_hours(hours_string, nominatim_object);
    // TODO: pass correct country code

    const open_next = oh.getNextChange();
    const open_next_text = this.getNextOpenDay(open_next) + this.addZero(open_next.getHours()) + ':' +
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

  private getNextOpenDay(open_next) {
    if (this.isSameDay(open_next, this.today)) {
      return 'heute um ';
    }
    if (this.isSameDay(open_next, this.tomorrow)) {
      return 'morgen um ';
    }
    return this.DAYS[open_next.getDay()] + ', ';
  }

  private isSameDay(d1, d2) {
    return d1.getFullYear() === d2.getFullYear() &&
      d1.getMonth() === d2.getMonth() &&
      d1.getDate() === d2.getDate();
  }

  private addZero(i) {
    if (i < 10) {
      i = '0' + i;
    }
    return i;
  }
}
