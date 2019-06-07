import {Injectable} from '@angular/core';
import * as opening_hours from 'opening_hours';

@Injectable({
  providedIn: 'root'
})
export class OpeningHoursService {

  constructor() {
  }

  getOpenNow(hours_string: string) {
    if (!hours_string) {
      return false;
    }
    const oh = new opening_hours(hours_string, null);
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

    const days = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
    const open_next = oh.getNextChange();
    const open_next_text = days[open_next.getDay()] + ', ' + this.addZero(open_next.getHours()) + ':' +
      this.addZero(open_next.getMinutes());

    return {
      open_now: oh.getState(),
      open_next: open_next_text
    };
  }

  private addZero(i) {
    if (i < 10) {
      i = '0' + i;
    }
    return i;
  }
}
