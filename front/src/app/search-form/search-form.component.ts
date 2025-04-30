import { Component, EventEmitter, Output } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
  Validators
} from '@angular/forms';
import {ApiService} from '../api-service.service';
import {Flight} from '../flight';
import {Router, RouterModule} from '@angular/router';
import {NgIf} from '@angular/common';
import { DataPassingService } from '../data-passing.service';
import { log } from 'node:console';

@Component({
  selector: 'app-search-form',
  imports: [ReactiveFormsModule, NgIf],
  standalone: true,
  templateUrl: './search-form.component.html',
  styleUrl: './search-form.component.css'
})
export class SearchFormComponent {
  @Output() searchStarted = new EventEmitter<void>();
  @Output() searchResults = new EventEmitter<Flight[]>();
  activeTab = 'have-flight';
  isLoading = false;
  submitted = false;
  flights: Flight[] = [];

  haveFlightForm: FormGroup;
  searchFlightForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private dataPassingService: DataPassingService,
    private router : Router
  ) {

    this.haveFlightForm = this.fb.group({
      tail_number: ['', Validators.required],
      scheduled_departure_local: ['', [this.dateTimeValidator]],
    });

    this.searchFlightForm = this.fb.group({
      depart_from: ['', [Validators.required]],
      arrive_at: ['', [Validators.required]],
      scheduled_departure_local :['', [this.dateTimeValidator]],
    });
  }

  switchTab(tabId: string) {
    this.submitted = false;
    this.activeTab = tabId;
  }

  log(){console.log('clicked');
  }
  // Passing the form's information to the service
  // In your component file
async formSubmitted() {
  this.searchStarted.emit();
  this.submitted = true;
  this.isLoading = true;
  
  const formGroup = this.activeTab === 'have-flight'
    ? this.haveFlightForm
    : this.searchFlightForm;
  
  console.log(this.dataPassingService.searchParams);

  formGroup.markAllAsTouched();
  if (formGroup.invalid) {
    this.isLoading = false; // Don't forget to reset loading state if form is invalid
    return;
  }

  this.dataPassingService.searchParams = formGroup.value;
  
  try {
    // Wait for the flight data to be fetched
    await this.dataPassingService.fetchFlightData();
    
    // Now we can safely access the flights after the API call completes
    this.searchResults.emit(this.dataPassingService.myFlights);
  } catch (error) {
    console.error('Error during flight search:', error);
    this.searchResults.emit([]); // Emit empty array on error
  } finally {
    this.isLoading = false; // Always reset loading state, whether successful or not
  }
}


  dateTimeValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;

    // Regular expression to match date and time format (e.g., YYYY-MM-DD)
    const dateTimeRegex = /^\d{4}-\d{2}-\d{2}?$/;

    if (!value || dateTimeRegex.test(value)) {
      return null; // Valid
    }

    return { invalidDateTime: 'Invalid date and time format.' };
  }
}
