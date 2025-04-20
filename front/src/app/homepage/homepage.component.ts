import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import {Flight} from '../flight';
import { SearchFormComponent} from '../search-form/search-form.component';

@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [RouterModule, ReactiveFormsModule, SearchFormComponent],
  templateUrl: './homepage.component.html',
  styleUrl: './homepage.component.css'
})
export class HomepageComponent {
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
