import { Component, EventEmitter, Output } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import {NgIf} from '@angular/common';
import {Flight} from '../flight';

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

  constructor(
    private fb: FormBuilder,
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

    // Build search parameters based on active tab
    const searchParams =
    {
      first_name: this.contactForm.value.first_name,
      last_name: this.contactForm.value.last_name,
      email: this.contactForm.value.email,
      topic: this.contactForm.value.topic,
      body: this.contactForm.value.body
    };
    console.log(searchParams);

    //Sending message to sky denied email
  }

}
