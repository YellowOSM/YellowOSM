import {NgModule} from '@angular/core';

import {
  MatIconModule,
  MatToolbarModule,
  MatInputModule,
  MatAutocompleteModule,
  MatButtonModule,
  MatSnackBarModule,
} from '@angular/material';

@NgModule({
  imports: [
    MatToolbarModule,
    MatIconModule,
    MatInputModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatSnackBarModule,
  ],
  exports: [
    MatToolbarModule,
    MatIconModule,
    MatInputModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatSnackBarModule,
  ]
})
export class MaterialModule {}
