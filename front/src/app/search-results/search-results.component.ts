import { Component, EventEmitter, Output } from '@angular/core';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-search-results',
  imports: [NgIf],
  templateUrl: './search-results.component.html',
  styleUrl: './search-results.component.css'
})
export class SearchResultsComponent {
  loaded: boolean = false;

  @Output() predictClicked = new EventEmitter<void>();
  @Output() notifyClicked = new EventEmitter<void>();

  triggerPredictionPopup() {
    this.predictClicked.emit();
  }

  triggerGetNotifiedPopup() {
    this.notifyClicked.emit();
  }
}
