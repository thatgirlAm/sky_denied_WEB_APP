import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import {NgClass, CommonModule, NgIf, DatePipe} from '@angular/common';
import { ApiService } from '../api-service.service';
import { DataPassingService } from '../data-passing.service';
import { Flight } from '../flight';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Prediction } from '../prediction';

@Component({
  selector: 'app-prediction-results',
  imports: [ NgIf, CommonModule ],
  templateUrl: './prediction-results.component.html',
  styleUrl: './prediction-results.component.css'
})
export class PredictionResultsComponent implements OnInit{
  prediction_loaded = false;
  flight!: Flight;
  prediction!: Prediction;
  predictionForm!: FormGroup;
  date !: any ; 
  
  ngOnInit(): void {
    this.flight = this.dataPassingService.selectedFlight ; 
    // console.log("Information");
    // console.log(this.flight);
    
    const date = new Date(this.flight.scheduled_departure_utc);
    const formattedDate = date.toISOString().split('T')[0]; 
    const formattedTime = date.toTimeString().split(':').slice(0, 2).join(':'); 
    const result = `${formattedDate} ${formattedTime}`;
    this.date = result;

    this.predictionForm = this.fb.group({
      main_scheduled_departure_utc: [result],
      mode: ["realtime"],
      tail_number: [this.flight.tail_number || ''] 
    });
    this.dataPassingService.predictionParams = this.predictionForm.value;
    // console.log("Paramètres de prediction");
    // console.log(this.dataPassingService.predictionParams);
    
    this.predict(); 
    //console.log(this.predictionForm);
    
  }

  @Output() closePopup = new EventEmitter<void>();
  constructor(private api:ApiService, private dataPassingService : DataPassingService, private fb: FormBuilder){

  }

  async predict() {
  this.prediction_loaded = false;
  
  try {
    // The key is using await here - this will pause execution until triggerPrediction resolves
    await this.dataPassingService.triggerPrediction();
    
    // Now we can safely access the prediction after the API call completes
    this.prediction = this.dataPassingService.prediction;
    this.prediction_loaded = true;
    console.log('Prediction loaded:', this.prediction);
  } catch (error) {
    console.error('Error during prediction:', error);
    this.prediction_loaded = true;
  }
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
