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
  public setFlights(){
    console.log('initialised');
    console.log(this.dataPassingService.searchParams);
    
    this.loaded = false
    if(this.dataPassingService.searchParams){
      this.dataPassingService.fetchFlightData(); 
      this.flights = this.dataPassingService.myFlights;
      this.loaded = true;
      console.log("from results:");  
      console.log(this.flights);
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['flights']) {
      this.loaded = !!this.flights && this.flights.length > 0;
    }
  }
  triggerPredictionPopup() {
    this.predictClicked.emit();
  }

  triggerGetNotifiedPopup() {
    this.notifyClicked.emit();
  }

  loadMoreResults() {
    console.log("Load more results triggered.");
    
  }
}
