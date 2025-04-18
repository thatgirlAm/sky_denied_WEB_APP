import { Component, EventEmitter, Output } from '@angular/core';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-prediction-results',
  imports: [ NgIf ],
  templateUrl: './prediction-results.component.html',
  styleUrl: './prediction-results.component.css'
})
export class PredictionResultsComponent {
  prediction_loaded = false;
  @Output() closePopup = new EventEmitter<void>();

  close() {
    this.closePopup.emit();
  }
}
