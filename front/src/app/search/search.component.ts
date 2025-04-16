import { Component } from '@angular/core';
import { SearchFormComponent } from '../search-form/search-form.component';
import { SearchResultsComponent } from '../search-results/search-results.component';
import { PredictionResultsComponent } from '../prediction-results/prediction-results.component';

@Component({
  selector: 'app-search',
  imports: [SearchFormComponent, SearchResultsComponent, PredictionResultsComponent],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css'
})
export class SearchComponent {

}
