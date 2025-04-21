import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ContactComponent } from '../contact/contact.component';

@Component({
  selector: 'app-about-us',
  imports: [RouterModule, ContactComponent],
  templateUrl: './about-us.component.html',
  styleUrl: './about-us.component.css'
})
export class AboutUsComponent {

}
