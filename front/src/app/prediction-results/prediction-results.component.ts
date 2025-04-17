import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-prediction-results',
  imports: [],
  templateUrl: './prediction-results.component.html',
  styleUrl: './prediction-results.component.css'
})
export class PredictionResultsComponent {
  @Output() closePopup = new EventEmitter<void>();

  close() {
    this.closePopup.emit();
  }
}
