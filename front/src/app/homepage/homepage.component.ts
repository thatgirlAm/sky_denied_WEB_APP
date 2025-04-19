import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ApiService } from '../api-service.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [RouterModule, ReactiveFormsModule], 
  templateUrl: './homepage.component.html',
  styleUrl: './homepage.component.css'
})
export class HomepageComponent {
  activeTab = 'have-flight';
  form: FormGroup;

  constructor(private api: ApiService, private fb: FormBuilder) {
    this.form = this.fb.group({
      tail_number: ['', Validators.required],
      scheduled_departure_local: ['', Validators.required],
      depart_from_iata: ['', [Validators.required, Validators.maxLength(3)]],
      arrive_at_iata: ['', [Validators.required, Validators.maxLength(3)]],
      flight_date: ['', Validators.required]
    });
  }

  fetchFlightData(): void {
    if (this.form.invalid) return;

    const tailNumber = this.form.value.tailNumber;
    this.api.searchFlights(tailNumber).subscribe({
      next: (flights) => {
        console.log('Flight Data:', flights);
        console.table(flights);
      },
      error: (err) => console.error('Error:', err)
    });
  }

  switchTab(tabId: string): void {
    this.activeTab = tabId;
  }
}