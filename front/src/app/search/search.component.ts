import { Component } from '@angular/core';
import { SearchFormComponent } from '../search-form/search-form.component';
import { SearchResultsComponent } from '../search-results/search-results.component';
import { PredictionResultsComponent } from '../prediction-results/prediction-results.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-search',
  imports: [SearchFormComponent, SearchResultsComponent, PredictionResultsComponent, CommonModule],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css'
})
export class SearchComponent {
  showPredictionPopup = false;

  handlePredictionTrigger() {
    this.showPredictionPopup = true;
  }

  closePredictionPopup() {
    console.log("Popup close handler triggered in search component");

    this.showPredictionPopup = false;
  }
}
