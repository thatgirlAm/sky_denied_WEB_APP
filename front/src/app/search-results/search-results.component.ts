import {Component, EventEmitter, Input, OnInit, Output, SimpleChanges} from '@angular/core';
import { NgFor, NgIf, CommonModule } from '@angular/common';
import { Flight } from '../flight';
import { DataPassingService } from '../data-passing.service';
import { log } from 'node:console';

@Component({
  selector: 'app-search-results',
  imports: [NgIf, NgFor, CommonModule],
  templateUrl: './search-results.component.html',
  styleUrl: './search-results.component.css'
})
export class SearchResultsComponent implements OnInit{
  @Input() flights: Flight[] | null = null;
  @Output() notifyClicked = new EventEmitter<void>();
  loaded: boolean = false;
  @Output() predictClicked = new EventEmitter<void>();
  
  constructor(private dataPassingService:DataPassingService){
  }
  ngOnInit(): void {
      this.setFlights();
      console.log("From results initialisation");
      console.log(this.flights);
  }
  public async setFlights() {
    console.log('initialised');
    console.log(this.dataPassingService.searchParams);
    
    this.loaded = false; // Set to false immediately to show loader
    
    if (this.dataPassingService.searchParams) {
      try {
        // IMPORTANT: Use await to wait for the Promise to resolve
        await this.dataPassingService.fetchFlightData();
        
        // Now that data is loaded, we can safely assign flights
        this.flights = this.dataPassingService.myFlights;
        console.log("from results:");  
        console.log(this.flights);
      } catch (error) {
        console.error('Error fetching flights:', error);
        this.flights = []; // Reset to empty array on error
      } finally {
        // Whether successful or not, set loaded to true when done
        this.loaded = true;
      }
    } else {
      // If there are no search params, immediately set loaded to true
      this.loaded = true;
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['flights']) {
      this.loaded = !!this.flights && this.flights.length > 0;
    }
  }
  triggerPredictionPopup(flight : Flight) {
    this.dataPassingService.selectedFlight = flight;
    this.predictClicked.emit();
  }

  triggerGetNotifiedPopup() {
    this.notifyClicked.emit();
  }

  loadMoreResults() {
    console.log("Load more results triggered.");
    
  }
}
