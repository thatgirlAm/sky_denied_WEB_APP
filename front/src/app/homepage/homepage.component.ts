import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ApiService } from '../api-service.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { log } from 'node:console';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [RouterModule, ReactiveFormsModule, NgIf], 
  templateUrl: './homepage.component.html',
  styleUrl: './homepage.component.css'
})
export class HomepageComponent {
  activeTab = 'have-flight';
  form: FormGroup;
  isLoading = false;
  constructor(private api: ApiService, private fb: FormBuilder) {
    this.form = this.fb.group({
      tail_number: ['', Validators.required],
      scheduled_departure_local: ['', Validators.required],
      depart_from_iata: ['', [Validators.required, Validators.maxLength(3)]],
      arrive_at_iata: ['', [Validators.required, Validators.maxLength(3)]],
      flight_date: ['', Validators.required]
    });
  }

  async fetchFlightData() {
    console.log("button clicked");
    
    if (this.form.invalid) return;

    const tailNumber = this.form.value.tailNumber;

    this.api.searchFlights(tailNumber).subscribe({
      next: (flights) => {
        this.isLoading = true ; 
        console.log('Flight Data:', flights);
        console.table(flights);
      },
      error: (err) => {
        console.error('Error:', err);
        this.isLoading = false;
  }});
  }

  switchTab(tabId: string): void {
    this.activeTab = tabId;
  }
}