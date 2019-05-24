import {NgModule} from '@angular/core';

import {
  MatIconModule,
  MatToolbarModule,
  MatInputModule,
  MatAutocompleteModule,
  MatButtonModule,
  MatSnackBarModule, MatChipsModule,
} from '@angular/material';

@NgModule({
  imports: [
    MatChipsModule,
    MatToolbarModule,
    MatIconModule,
    MatInputModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatSnackBarModule,
  ],
  exports: [
    MatChipsModule,
    MatToolbarModule,
    MatIconModule,
    MatInputModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatSnackBarModule,
  ]
})
export class MaterialModule {}
