import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {YellowmapComponent} from './yellowmap/yellowmap.component';
import {AboutComponent} from './about/about.component';
import {PageNotFoundComponent} from './page-not-found/page-not-found.component';

const routes: Routes = [
  {path: 'map/:zoom/:lat/:lon', component: YellowmapComponent},
  {path: 'about', component: AboutComponent},
  {path: '', redirectTo: '/map/16/47.0707/15.4395', pathMatch: 'full'},
  {path: '**', component: PageNotFoundComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}

