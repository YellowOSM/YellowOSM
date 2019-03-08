import {NgModule} from '@angular/core';

import {
  MatIconModule,
  MatToolbarModule,
  MatInputModule,
  MatAutocompleteModule,
} from '@angular/material';

@NgModule({
  imports: [
    MatToolbarModule,
    MatIconModule,
    MatInputModule,
    MatAutocompleteModule,
  ],
  exports: [
    MatToolbarModule,
    MatIconModule,
    MatInputModule,
    MatAutocompleteModule,
  ]
})
export class MaterialModule {}
