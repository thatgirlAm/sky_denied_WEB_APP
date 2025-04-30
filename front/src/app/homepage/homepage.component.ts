import { Component, EventEmitter, Input, Output } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule, NgIf } from '@angular/common';
import {Flight} from '../flight';
import { SearchFormComponent} from '../search-form/search-form.component';
import { ApiService } from '../api-service.service';
import { ToastrService } from 'ngx-toastr';
import { SearchResultsComponent } from '../search-results/search-results.component';
import { PredictionResultsComponent } from '../prediction-results/prediction-results.component';
import { InputEmailFormComponent } from '../input-email-form/input-email-form.component';

@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [RouterModule, CommonModule, ReactiveFormsModule, SearchResultsComponent, PredictionResultsComponent,InputEmailFormComponent, SearchFormComponent],
  templateUrl: './homepage.component.html',
  styleUrl: './homepage.component.css'
})
export class HomepageComponent {

  activeTab: string = 'have-flight';
  loader: boolean = false;
  //flights : Flight[] = []; 
  showTable : boolean = false ; 
  @Input() flights: Flight[] = [];
  @Output() predictClicked = new EventEmitter<Flight>();
  @Output() notifyClicked = new EventEmitter<Flight>();
  showPredictionPopup = false;
  showGetNotifiedPopup = false;
  searchClicked = false ;
  searchResults: Flight[] = this.flights;
  searchForm !: FormGroup ; 

  // to know if the model has been triggered
  isModelTriggering = false;
  previousSearch = false ; 
  searchParams !: any ; 
  isLoading = false;
  submitted = false;


  constructor(private fb: FormBuilder, private apiService: ApiService, private toastrService: ToastrService) {}

  handleSearchStarted() {
  this.searchClicked = true;
  this.searchResults = [];
  }

  handleSearchResults(flights: Flight[]) {
  this.searchResults = flights;
  this.searchClicked = true;
  }


  handlePredictionTrigger() {
    this.searchClicked = true ;
    this.showPredictionPopup = true;
  }

  closePredictionPopup() {
    this.showPredictionPopup = false;
  }

  handleGetNotifiedTrigger() {
    console.log('Get Notified Triggered');

    this.showGetNotifiedPopup = true;
  }

  closeGetNotifiedPopup() {
    console.log('Get Notified closed');

    this.showGetNotifiedPopup = false;
  }



}
