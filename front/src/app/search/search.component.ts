import { Component } from '@angular/core';
import { SearchFormComponent } from '../search-form/search-form.component';
import { SearchResultsComponent } from '../search-results/search-results.component';
import { PredictionResultsComponent } from '../prediction-results/prediction-results.component';
import { InputEmailFormComponent } from '../input-email-form/input-email-form.component';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api-service.service';
import { ToastrService } from 'ngx-toastr';
import { Router } from '@angular/router';
import { Flight } from '../flight';
import { Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-search',
  imports: [SearchFormComponent, SearchResultsComponent, PredictionResultsComponent,InputEmailFormComponent,  CommonModule],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css'
})
export class SearchComponent {
  @Input() flights: Flight[] = [];
  @Output() predictClicked = new EventEmitter<Flight>();
  @Output() notifyClicked = new EventEmitter<Flight>();
  showPredictionPopup = false;
  showGetNotifiedPopup = false;
  searchClicked = false ;
  searchResults: Flight[] = [];

  // to know if the model has been triggered
  isModelTriggering = false;

  searchParams !: any ; 

  constructor(private apiService: ApiService, private toastr: ToastrService, private router: Router) {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state) {
      this.flights = navigation.extras.state['flights'];
      this.searchParams = navigation.extras.state['searchParams'];
    }
    console.log(this.flights);
    
  }


// Charlotte's functions

  handleSearchStarted() {
    this.searchClicked = true;
    this.searchResults = [];
  }

  handleSearchResults(flights: Flight[]) {
    this.searchResults = flights;
  }

  handlePredictionTrigger() {
    this.searchClicked = true ;
    //this.trigger_model();
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
