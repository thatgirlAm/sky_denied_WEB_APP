import { Component } from '@angular/core';
import { SearchFormComponent } from '../search-form/search-form.component';
import { SearchResultsComponent } from '../search-results/search-results.component';
import { PredictionResultsComponent } from '../prediction-results/prediction-results.component';
import { InputEmailFormComponent } from '../input-email-form/input-email-form.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-search',
  imports: [SearchFormComponent, SearchResultsComponent, PredictionResultsComponent, InputEmailFormComponent, CommonModule],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css'
})
export class SearchComponent {
  showPredictionPopup = false;
  showGetNotifiedPopup = false;

  handlePredictionTrigger() {
    this.showPredictionPopup = true;
  }

  closePredictionPopup() {
    this.showPredictionPopup = false;
  }

  handleGetNotifiedTrigger() {
    console.log('Get Notified Triggered');

    this.showGetNotifiedPopup = true;
  }

  closeGetNotifiedPopup() {
    console.log('Get Notified closed');

    this.showGetNotifiedPopup = false;
  }
}
