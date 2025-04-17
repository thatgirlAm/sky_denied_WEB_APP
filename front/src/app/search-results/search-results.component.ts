import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-search-results',
  imports: [],
  templateUrl: './search-results.component.html',
  styleUrl: './search-results.component.css'
})
export class SearchResultsComponent {
  @Output() predictClicked = new EventEmitter<void>();
  @Output() notifyClicked = new EventEmitter<void>();

  triggerPredictionPopup() {
    this.predictClicked.emit();
  }

  triggerGetNotifiedPopup() {
    this.notifyClicked.emit();
  }
}
