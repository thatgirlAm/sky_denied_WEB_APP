import {Component, EventEmitter, Input, OnInit, Output, SimpleChanges} from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { Flight } from '../flight';
import { DataPassingService } from '../data-passing.service';

@Component({
  selector: 'app-search-results',
  imports: [NgIf, NgFor],
  templateUrl: './search-results.component.html',
  styleUrl: './search-results.component.css'
})
export class SearchResultsComponent implements OnInit{

  @Input() flights: Flight[] | null = null;
  @Output() notifyClicked = new EventEmitter<void>();
  loaded: boolean = false;
  @Output() predictClicked = new EventEmitter<void>();
  
  constructor(private dataPassingService:DataPassingService){}
  ngOnInit(): void {
      this.setFlights();
      console.log(this.flights);
      
  }
  public setFlights(){
    this.loaded = false
    if(this.dataPassingService.searchParams){
      this.dataPassingService.fetchFlightData(); 
      this.flights = this.dataPassingService.myFlights;
      this.loaded = true;
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
