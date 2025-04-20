import {Component, EventEmitter, Input, Output, SimpleChanges} from '@angular/core';
import { NgIf } from '@angular/common';
import { Flight } from '../flight';

@Component({
  selector: 'app-search-results',
  imports: [NgIf],
  templateUrl: './search-results.component.html',
  styleUrl: './search-results.component.css'
})
export class SearchResultsComponent {
  @Input() flights: Flight[] | null = null;
  loaded: boolean = false;

  @Output() predictClicked = new EventEmitter<void>();
  @Output() notifyClicked = new EventEmitter<void>();


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
}
