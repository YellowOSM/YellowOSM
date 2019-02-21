import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {YellowmapComponent} from './yellowmap/yellowmap.component';
import {PageNotFoundComponent} from './page-not-found/page-not-found.component';
import {Geo58RedirectComponent} from './geo58-redirect/geo58-redirect.component';

const routes: Routes = [
  {path: ':geo58', component: Geo58RedirectComponent},
  {path: ':zoom/:lat/:lon', component: YellowmapComponent},
  {path: '', redirectTo: '/14/47.0707/15.4395', pathMatch: 'full'},
  {path: '**', component: PageNotFoundComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}

