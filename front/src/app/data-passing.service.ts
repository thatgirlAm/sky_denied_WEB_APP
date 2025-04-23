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

  fetchFlightData(){
    this.api.searchFlights(this.searchParams).subscribe({
          next: (flights: Flight[]) => {
            //console.log('Flight Data:', flights);
            console.table("fetch data called");
            this.myFlights = flights;
            //console.log(this.myFlights);
            //this.searchResults.emit(flights);
           },
           error: (err) => {
            //this.searchResults.emit([]);
           }
         });
  }

  triggerPrediction() {
    console.log(this.predictionParams);
    
    this.api.postPrediction(this.predictionParams).subscribe({
      next: (response: any ) => {
        console.log('Prediction response:', response);
        if (response && response.data) {
          this.prediction = response.data.message;
        } else {
          this.toastr.warning('Prediction data format unexpected');
        }
      },
      error: (err:any) => {
        this.toastr.error("Failed to get prediction");
        console.error('Prediction error:', err);
      }
    });
  }
}
