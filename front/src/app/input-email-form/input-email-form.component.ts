import {Component, EventEmitter, Output} from '@angular/core';

@Component({
  selector: 'app-input-email-form',
  imports: [],
  templateUrl: './input-email-form.component.html',
  styleUrl: './input-email-form.component.css'
})
export class InputEmailFormComponent {
  @Output() closeGetNotifiedPopup = new EventEmitter<void>();

  close() {
    this.closeGetNotifiedPopup.emit();
  }
}
