import { Component, OnInit } from '@angular/core';
import {Geo58Service} from '../services/geo58.service';
import {ActivatedRoute, Router} from '@angular/router';

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
  ) { }

  ngOnInit() {
    let geo58hash: string = this.route.snapshot.paramMap.get('geo58');
    console.log('input:\n' + geo58hash);
    console.log('output:\n' + this.geo58.toZoomLatLon(geo58hash));
  }
}
