import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {YellowmapComponent} from './yellowmap/yellowmap.component';
import {AboutComponent} from './about/about.component';

const routes: Routes = [
  {path: '', redirectTo: '/map/15.4395/47.0707/16', pathMatch: 'full'},
  {path: 'map/:lon/:lat/:zoom', component: YellowmapComponent},
  {path: 'about', component: AboutComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}

