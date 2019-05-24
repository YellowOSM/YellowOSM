import {Component, Input, OnInit} from '@angular/core';

@Component({
  selector: 'app-location-list',
  templateUrl: './location-list.component.html',
  styleUrls: ['./location-list.component.scss']
})
export class LocationListComponent implements OnInit {

  @Input() features = [];

  constructor() {
  }

  ngOnInit() {
  }

}
