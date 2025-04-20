import { Component } from '@angular/core';

import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { SearchFormComponent } from '../search-form/search-form.component';

@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [SearchFormComponent, RouterModule, ReactiveFormsModule, NgIf],

  templateUrl: './homepage.component.html',
  styleUrl: './homepage.component.css'
})
export class HomepageComponent {

  searchForm: FormGroup;
  haveFlightForm: FormGroup;
  activeTab: string = 'have-flight';
  loader: boolean = false;
  flights : Flight[] = []; 
  showTable : boolean = false ; 
  
  constructor(private fb: FormBuilder, private apiService: ApiService, private toastrService: ToastrService) {
    this.searchForm = this.fb.group({
      departure: ['', Validators.required],
      arrival: ['', Validators.required],
      date: ['', [Validators.required, Validators.pattern(/^\d{8}$/)]], 
    });

    this.haveFlightForm = this.fb.group({
      flightNumber: ['', Validators.required],
      date: ['', [Validators.required, Validators.pattern(/^\d{8}$/)]],
    });
  }
  
  switchTab(tabId: string) {
    this.activeTab = tabId;
  }

  onSubmitSearch(): void {
    if (this.searchForm.valid) {
      this.loader = true;
      const searchObject = this.searchForm.value;
      this.apiService.PostData('search-flight', searchObject).subscribe({
        next: (data) => {
          console.log('Search result:', data);
          this.flights = data['flights']; 
          this.showTableFunction(); 
          this.loader = false;
        },
        error: (err) => {
          console.error('Error occurred:', err);
          this.toastrService.error('There is an error: ', err); 
          this.loader = false;
        },
      });
    } else {
      console.warn('Search form is invalid');
    }
  }

  onSubmitHaveFlight(): void {
    if (this.haveFlightForm.valid) {
      this.loader = true;
      const flightDetails = this.haveFlightForm.value;
      this.apiService.PostData('have-flight', flightDetails).subscribe({
        next: (data) => {
          console.log('Flight details submitted:', data);
          this.loader = false;
        },
        error: (err) => {
          console.error('Error occurred:', err);
          this.loader = false;
        },
      });
    } else {
      console.warn('Have flight form is invalid');
    }
  }


  showTableFunction():void{
    if(this.loader==false)
    {
      this.showTable = true ; 
  }

}
}