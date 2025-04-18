import { Component } from '@angular/core';
import { SearchFormComponent } from '../search-form/search-form.component';
import { SearchResultsComponent } from '../search-results/search-results.component';
import { PredictionResultsComponent } from '../prediction-results/prediction-results.component';
import { InputEmailFormComponent } from '../input-email-form/input-email-form.component';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api-service.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-search',
  imports: [SearchFormComponent, SearchResultsComponent, PredictionResultsComponent, InputEmailFormComponent, CommonModule],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css'
})
export class SearchComponent {
  showPredictionPopup = false;
  showGetNotifiedPopup = false;
  searchClicked = false ;
  // to know if the model has been triggered
  isModelTriggering = false;

  constructor(private apiService: ApiService, private toastr: ToastrService) {}


  // TODO : I do not understand Charlotte's logic here
  trigger_model(data:any) {
    this.isModelTriggering = true;
    const triggerEndpoint = 'trigger/data';
    const triggerData = data;
    // TODO : validate the format of the data (from the form)
    this.apiService.PostMessage(triggerEndpoint, triggerData).subscribe({
      next: (res: any) => {
        this.toastr.success('Model triggered successfully: ' + res);
        this.isModelTriggering = false;
      },
      error: (err: any) => {
        this.toastr.error('Error triggering model: ' + err.message);
        this.isModelTriggering = false;
      }
    });
  }


// Charlotte's functions
  handlePredictionTrigger() {
    this.searchClicked = true ;
    //this.trigger_model();
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
