import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgIf } from '@angular/common';
import {Flight} from '../flight';
import { SearchFormComponent} from '../search-form/search-form.component';
import { ApiService } from '../api-service.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [RouterModule, ReactiveFormsModule, SearchFormComponent],
  templateUrl: './homepage.component.html',
  styleUrl: './homepage.component.css'
})
export class HomepageComponent {

  activeTab: string = 'have-flight';
  loader: boolean = false;
  flights : Flight[] = []; 
  showTable : boolean = false ; 

  constructor(private fb: FormBuilder, private apiService: ApiService, private toastrService: ToastrService) {}


  searchClicked = false ;
  searchResults: Flight[] = [];

  handleSearchStarted() {
  this.searchClicked = true;
  this.searchResults = [];
  }

  handleSearchResults(flights: Flight[]) {
  this.searchResults = flights;
  this.searchClicked = true;
  }

}
