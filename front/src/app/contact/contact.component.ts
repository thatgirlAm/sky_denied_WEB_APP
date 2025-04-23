import { Component, EventEmitter, Output } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import {NgIf} from '@angular/common';
import {Flight} from '../flight';
import { ApiService } from '../api-service.service';

@Component({
  selector: 'app-contact',
  imports: [ReactiveFormsModule, NgIf],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.css'
})
export class ContactComponent {
  isLoading = false;
  submitted = false;
  contactForm: FormGroup;
  sent :boolean = false ; 
  constructor(
    private fb: FormBuilder,
    private api: ApiService
  ) {
    this.contactForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', Validators.required],
      topic: ['', Validators.required],
      body: ['', Validators.required],
    });
  }


  contactFormSubmit() {
    this.submitted = true;
    this.contactForm.markAllAsTouched();

    if (this.contactForm.invalid) return;

    const searchParams = {
      name: this.contactForm.value.first_name + this.contactForm.value.last_name,
      email: this.contactForm.value.email,
      topic: this.contactForm.value.topic,
      body: this.contactForm.value.body,
    };

    this.isLoading = true; 
    this.api.postContact(searchParams).subscribe({
      next: (res) => {
        if (res) {
          this.sent = true;
          console.log('Contact form sent successfully:', searchParams);
        } else {
          console.error('Failed to send contact form');
        }
      },
      error: (err) => {
        console.error('An error occurred:', err);
      },
      complete: () => {
        this.isLoading = false; 
      },
    });
  }

}
