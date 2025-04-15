import { Routes } from '@angular/router';
import { AboutUsComponent } from './about-us/about-us.component';
import { OurModelComponent } from './our-model/our-model.component';
import { SearchResultsComponent } from './search-results/search-results.component';
import { HomepageComponent } from './homepage/homepage.component';


export const routes: Routes = [
  { path: '', redirectTo: 'homepage', pathMatch: 'full' },
  { path: 'homepage', component: HomepageComponent  },
  { path: 'about-us', component: AboutUsComponent },
  { path: 'our-model', component: OurModelComponent },
  { path: 'search-results', component: SearchResultsComponent },
];
