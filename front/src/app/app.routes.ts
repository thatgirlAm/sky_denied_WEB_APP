import { Routes } from '@angular/router';
import { AboutUsComponent } from './about-us/about-us.component';
import { OurModelComponent } from './our-model/our-model.component';
import { HomepageComponent } from './homepage/homepage.component';
import { SearchComponent } from './search/search.component';
import { SearchFormComponent } from './search-form/search-form.component';
import { SearchResultsComponent } from './search-results/search-results.component';
import { PredictionResultsComponent } from './prediction-results/prediction-results.component';
import { InputEmailFormComponent } from './input-email-form/input-email-form.component';
import { ContactComponent } from './contact/contact.component';

export const routes: Routes = [
  { path: '', redirectTo: 'homepage', pathMatch: 'full' },
  { path: 'homepage', component: HomepageComponent, children: [
      { path: 'search-form', component: SearchFormComponent },
    ] },
  { path: 'about-us', component: AboutUsComponent, children: [
      { path: 'contact', component: ContactComponent },
    ]
  },
  { path: 'our-model', component: OurModelComponent },
  {
    path: 'search',
    component: SearchComponent,
    children: [
      { path: 'search-form', component: SearchFormComponent },
      { path: 'search-results', component: SearchResultsComponent, children: [
          { path: 'prediction-results', component: PredictionResultsComponent },
          { path: 'get-notify', component: InputEmailFormComponent },
        ]
      },
    ]
  },
];
