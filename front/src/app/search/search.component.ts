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
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';


@Component({
  selector: 'app-search',
  imports: [SearchFormComponent, ReactiveFormsModule, SearchResultsComponent, PredictionResultsComponent,InputEmailFormComponent,  CommonModule],
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
  searchResults: Flight[] = this.flights;
  searchForm !: FormGroup ; 

  // to know if the model has been triggered
  isModelTriggering = false;
  previousSearch = false ; 
  searchParams !: any ; 
  isLoading = false;
  submitted = false;

  constructor(private apiService: ApiService, private toastr: ToastrService, private router: Router, private fb:FormBuilder) {
    
   
  }

// Charlotte's functions

  handleSearchStarted() {
    this.searchClicked = true;
    this.searchResults = [];
  }

  handleSearchResults(flights: Flight[]) {
    this.searchResults = flights;
    this.searchClicked = true;
  }

  handlePredictionTrigger() {
    this.searchClicked = true ;
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



  dateTimeValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;

    // Regular expression to match date and time format (e.g., YYYY-MM-DD HH:mm:ss)
    const dateTimeRegex = /^\d{4}-\d{2}-\d{2}?$/;

    if (!value || dateTimeRegex.test(value)) {
        return null; // Valid
    }

    return { invalidDateTime: 'Invalid date and time format. Use YYYY-MM-DD HH:mm:ss' }; // Invalid
}

}
