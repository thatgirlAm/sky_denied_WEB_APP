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
  searchResults: Flight[] = [];
  searchForm !: FormGroup ; 

  // to know if the model has been triggered
  isModelTriggering = false;

  previousSearch = false ; 
  searchParams !: any ; 
  isLoading = false;
  submitted = false;

  constructor(private apiService: ApiService, private toastr: ToastrService, private router: Router, private fb:FormBuilder) {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state) {
      this.flights = navigation.extras.state['flights'];
      this.searchParams = navigation.extras.state['searchParams'];
    }
    console.log(this.flights);

    this.searchForm = this.fb.group({
      tail_number: ['', Validators.required],
      scheduled_departure_local: ['', [this.dateTimeValidator]],


    });
    
  }

*/
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


  fetchFlightData() {
    this.submitted = true;
    const formGroup = this.searchForm ; 

    formGroup.markAllAsTouched();
    if (formGroup.invalid) return;
  
    this.isLoading = true;
  
    // Build search parameters based on active tab
    // const searchParams = this.activeTab === 'have-flight' 
    //   ? { tail_number: this.haveFlightForm.value.tail_number }
    //   : { 
    //       depart_from: this.searchFlightForm.value.depart_from_iata,
    //       arrive_at: this.searchFlightForm.value.arrive_at_iata
    //     };
  
    // this.apiService.searchFlights(searchParams).subscribe({
    //   next: (flights: Flight[]) => {
    //     console.log('Search Params:', searchParams);
    //     console.log('Flights:', flights);
        
    //     this.isLoading = false;
    //     this.submitted = false;
  
    //     // Add null check for flights
    //     if (flights && flights.length > 0) {
    //       this.router.navigate(['search'], {
    //         state: {
    //           flights: flights,
    //           searchParams: searchParams
    //         }
    //       }).catch(error => {
    //         console.error('Navigation error:', error);
    //         // Handle navigation error (e.g., show error message)
    //       });
    //     } else {
    //       // Handle no results case
    //       console.warn('No flights found');
    //       // Optionally show message to user
    //     }
    //   },
    //   error: (err) => {
    //     console.error('API Error:', err);
    //     this.isLoading = false;
    //     this.submitted = false;
    //     // Optionally show error message to user
    //   }
    // });
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
