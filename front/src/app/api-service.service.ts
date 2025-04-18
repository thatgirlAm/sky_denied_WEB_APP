// Instpired by daisy : https://github.com/thatgirlAm/daisy/blob/main/src/app/base/api.service.ts
// -- Author : Amaëlle DIOP -- // 

import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr'; 
import { Inject } from '@angular/core';
import { lastValueFrom, Observable} from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})

export class ApiService {
  url : string  = 'http://127.0.0.1:8000/api/';
  data!: string | null;


  constructor(private router: Router, private http: HttpClient, @Inject(ToastrService) private toastr: ToastrService) { 
  }
/*
   public getFunction(url_:string)
   {
    this.http.get<any[]>(this.url+ url_).subscribe({
      next: (res:any)=>{
        return res;
      }
    });
   }

*/

// function to get the "data" part of the api response for a "get" function
   getData(url_: string) {
    this.http.get<any>(this.url+url_).subscribe({
      next : (res:any) =>{
        return res.data
      } ,
      error : (err) => 
        {
          return this.toastr.error(err);
        }
    })
  }

// function to get the "status" part of the api response for a "get" function
  getStatus(url_: string) {
    this.http.get<any>(this.url+url_).subscribe({
      next : (res:any) =>{
        return res.status
      } ,
      error : (err) => 
        {
          return this.toastr.error(err);
        }
    })
    } 
  // function to get the "message" part of the api response for a "get" function
  getMessage(url_: string) {
    this.http.get<any>(this.url+url_).subscribe({
      next : (res:any) =>{
        return res.message
      } ,
      error : (err) => 
        {
          return this.toastr.error(err);
        }
    })
    } 
  
// function to get the "status" part of the api response for a "post" function
  PostStatus(url_: string, data: any) :Observable<any>{
    return this.http.post<any>(this.url + url_, data).pipe(
      map((res: any) => res.status)
    );
    }

// function to get the "data" part of the api response for a "post" function
PostData(url_: string, data: any): Observable<any> {
  return this.http.post<any>(this.url + url_, data).pipe(
    map((res: any) => res.data)
  );
}


// function to get the "message" part of the api response for a "post" function
PostMessage(url_: string, data: any): Observable<any> {
  return this.http.post<any>(this.url + url_, data).pipe(
    map((res: any) => res.message)
  );
}

  
}