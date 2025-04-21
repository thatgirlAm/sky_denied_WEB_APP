import { Injectable } from '@angular/core';
import { Flight } from './flight';
import { FormGroup } from '@angular/forms';
import { log } from 'node:console';
import { ApiService } from './api-service.service';

@Injectable({
  providedIn: 'root'
})
export class DataPassingService {

  public myFlights!: Flight[];
  public searchParams !: FormGroup<any> ; 
  constructor(private api: ApiService) {}

  fetchFlightData(){
    this.api.searchFlights(this.searchParams).subscribe({
          next: (flights: Flight[]) => {
            //console.log('Flight Data:', flights);
            console.table("fetch data called");
            this.myFlights = flights;
            console.log(this.myFlights);
            //this.searchResults.emit(flights);
           },
           error: (err) => {
            //this.searchResults.emit([]);
           }
         });
  }

  // fetchFlightData() {
  //   this.submitted = true;
  //   const formGroup = this.activeTab === 'have-flight'
  //     ? this.haveFlightForm
  //     : this.searchFlightForm;

  //   formGroup.markAllAsTouched();
  //   if (formGroup.invalid) return;

  //   this.isLoading = true;
  //   this.searchStarted.emit();

  //   // Build search parameters based on active tab
  //   const searchParams = this.activeTab === 'have-flight'
  //     ? { tail_number: this.haveFlightForm.value.tail_number }
  //     : {
  //       depart_from: this.searchFlightForm.value.depart_from,
  //       arrive_at: this.searchFlightForm.value.arrive_at
  //     };
  //   console.log(searchParams);


  //   this.api.searchFlights(searchParams).subscribe({
  //     next: (flights: Flight[]) => {
  //       console.log('Flight Data:', flights);
  //       console.table(flights);
  //       this.isLoading = false;
  //       this.submitted = false;
  //       this.searchResults.emit(flights);
  //     },
  //     error: (err) => {
  //       this.isLoading = false;
  //       this.submitted = false;
  //       this.searchResults.emit([]);
  //     }
  //   });
  // }
  
}
