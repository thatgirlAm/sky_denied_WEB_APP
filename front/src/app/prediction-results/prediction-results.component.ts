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
    
    const date = new Date(this.flight.scheduled_departure_local);
    const formattedDate = date.toISOString().split('T')[0]; 
    const formattedTime = date.toTimeString().split(':').slice(0, 2).join(':'); 
    const result = `${formattedDate} ${formattedTime}`;
    console.log(result); 

    this.predictionForm = this.fb.group({
      main_scheduled_departure_utc: [result],
      mode: ["realtime"],
      tail_number: [this.flight.tail_number || ''] 
    });
    this.dataPassingService.predictionParams = this.predictionForm.value;
    this.predict(); 
    console.log(this.predictionForm);
    
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
    }, 3000); 
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
