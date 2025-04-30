import { Injectable } from '@angular/core';
import { Flight } from './flight';
import { FormGroup } from '@angular/forms';
import { log } from 'node:console';
import { ApiService } from './api-service.service';
import { Prediction } from './prediction';
import { ToastrService } from 'ngx-toastr';


@Injectable({
  providedIn: 'root'
})
export class DataPassingService {

  public myFlights!: Flight[];
  public searchParams !: FormGroup<any> ; 
  public predictionParams !: FormGroup<any>;
  public prediction !: Prediction ; 
  public selectedFlight !: Flight ; 
  constructor(private api: ApiService, private toastr: ToastrService) {}

  fetchFlightData(): Promise<Flight[]> {
    return new Promise((resolve, reject) => {
      this.api.searchFlights(this.searchParams).subscribe({
        next: (flights: Flight[]) => {
          console.table("fetch data called");
          this.myFlights = flights;
          resolve(flights);  // Resolve the promise with the flights data
        },
        error: (err) => {
          console.error('Error fetching flights:', err);
          this.myFlights = [];  // Reset to empty array on error
          reject(err);  // Reject the promise with the error
        }
      });
    });
  }
  triggerPrediction(): Promise<any> {
    return new Promise((resolve, reject) => {
      this.api.postPrediction(this.predictionParams).subscribe({
        next: (response: any) => {
          console.log('Prediction response:', response);
          if (response && response.data) {
            this.prediction = response.data;
            resolve(this.prediction); 
          } else {
            this.toastr.warning('Prediction data format unexpected');
            reject('Unexpected data format');
          }
        },
        error: (err: any) => {
          this.toastr.error("Failed to get prediction");
          console.error('Prediction error:', err);
          reject(err);
        }
      });
    });
  }
}
