import {Component, OnInit} from '@angular/core';
import {Geo58Service} from '../services/geo58.service';
import {ActivatedRoute, NavigationExtras, Router} from '@angular/router';

@Component({
  selector: 'app-geo58-redirect-component',
  templateUrl: './geo58-redirect.component.html',
  styleUrls: ['./geo58-redirect.component.scss']
})
export class Geo58RedirectComponent implements OnInit {

  constructor(
    private geo58: Geo58Service,
    private router: Router,
    private route: ActivatedRoute
  ) {
  }

  ngOnInit() {
    const geo58hash: string = this.route.snapshot.paramMap.get('geo58');
    console.log('input:\n' + geo58hash);
    this.geo58.toZoomLatLon(geo58hash)
      .subscribe(
        resolvedHash => {
          const navigationExtras: NavigationExtras = {
            queryParams: { 'amenity': this.route.snapshot.paramMap.get('amenity') },
          };
          console.log('amenity in redirecter:' + this.route.snapshot.paramMap.get('amenity'));
          this.router.navigate([resolvedHash['zoom'], resolvedHash['x'], resolvedHash['y'],
            {amenity: this.route.snapshot.paramMap.get('amenity')}]);
        },
        error => {
          console.log(error);
          this.router.navigate(['/doesnotexist']);
        });
  }
}
