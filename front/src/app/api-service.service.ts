// Instpired by daisy : https://github.com/thatgirlAm/daisy/blob/main/src/app/base/api.service.ts
// -- Author : Amaëlle DIOP -- // 

import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr'; 
import { Inject } from '@angular/core';
import { lastValueFrom, Observable} from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Flight } from './flight';


@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = 'http://127.0.0.1:8000/api/';

  constructor(
    private http: HttpClient,
    private toastr: ToastrService,
    private router: Router
  ) {}

  // Generic POST method
  post<T>(endpoint: string, body: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, body).pipe(
      catchError(err => {
        this.toastr.error('Request failed');
        throw err;
      })
    );
  }

  // Specific flight search method
  searchFlights(tailNumber: string): Observable<Flight[]> {
    return this.post<Flight[]>('flights/search/', { tail_number: tailNumber });
  }

  // Test method
  testMessage(): void {
    this.http.get<{ message: string }>(`${this.baseUrl}test`).subscribe({
      next: (res) => this.toastr.success(res.message),
      error: (err) => this.toastr.error('Test failed')
    });
  }
}