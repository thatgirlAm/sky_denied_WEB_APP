import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import {NgClass, CommonModule, NgIf, DatePipe} from '@angular/common';
import { ApiService } from '../api-service.service';
import { DataPassingService } from '../data-passing.service';
import { Flight } from '../flight';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Prediction } from '../prediction';

@Component({
  selector: 'app-prediction-results',
  imports: [ NgIf, NgClass, DatePipe ],
  templateUrl: './prediction-results.component.html',
  styleUrl: './prediction-results.component.css'
})
export class PredictionResultsComponent implements OnInit{
  prediction_loaded = false;
  flight!: Flight;
  prediction!: Prediction;
  predictionForm!: FormGroup;
  
  ngOnInit(): void {
    this.flight = this.dataPassingService.selectedFlight ; 
    this.predictionForm = this.fb.group({
      flight_number: [this.flight.flight_number_iata],
      departure_date: [new Date(this.flight.scheduled_departure_local).toISOString().split('T')[0]],
      tail_number: [this.flight.tail_number || ''] 
    });
    this.dataPassingService.predictionParams = this.predictionForm;
    this.predict(); 
  }

  @Output() closePopup = new EventEmitter<void>();
  constructor(private api:ApiService, private dataPassingService : DataPassingService, private fb: FormBuilder){}
  predict() {
    this.prediction_loaded = false;
    this.dataPassingService.triggerPrediction();
    
    // Subscribe to the prediction result or use a timeout to simulate loading
    setTimeout(() => {
      this.prediction = this.dataPassingService.prediction;
      this.prediction_loaded = true;
      console.log('Prediction loaded:', this.prediction);
    }, 3000); // Simulating 3 seconds loading time
  }

  close() {
    this.closePopup.emit();
  }
  
  // Helper to get delay message for display
  getDelayMessage() {
    if (!this.prediction) return '';
    
    if (this.prediction.delayed) {
      return this.prediction.message || 'Delay expected';
    } else {
      return 'On time';
    }
  }


}
