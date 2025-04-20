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
import {RouterModule} from '@angular/router';
import {NgIf} from '@angular/common';

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
    private api: ApiService
  ) {
    this.haveFlightForm = this.fb.group({
      tail_number: ['', Validators.required],
      scheduled_departure_local_have_flight: ['', [this.dateTimeValidator]],

    });

    this.searchFlightForm = this.fb.group({
      depart_from: ['', [Validators.required]],
      arrive_at: ['', [Validators.required]],
      scheduled_departure_local_outbound: ['', [this.dateTimeValidator]],
    });
  }

  fetchFlightData() {
    this.submitted = true;
    const formGroup = this.activeTab === 'have-flight'
      ? this.haveFlightForm
      : this.searchFlightForm;

    formGroup.markAllAsTouched();
    if (formGroup.invalid) return;

    this.isLoading = true;
    this.searchStarted.emit();

    // Build search parameters based on active tab
    const searchParams = this.activeTab === 'have-flight'
      ? { tail_number: this.haveFlightForm.value.tail_number }
      : {
        depart_from: this.searchFlightForm.value.depart_from,
        arrive_at: this.searchFlightForm.value.arrive_at
      };
    console.log(searchParams);


    this.api.searchFlights(searchParams).subscribe({
      next: (flights: Flight[]) => {
        console.log('Flight Data:', flights);
        console.table(flights);
        this.isLoading = false;
        this.submitted = false;
        this.searchResults.emit(flights);
      },
      error: (err) => {
        this.isLoading = false;
        this.submitted = false;
        this.searchResults.emit([]);
      }
    });
  }
  switchTab(tabId: string) {
    this.submitted = false;
    this.activeTab = tabId;
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
