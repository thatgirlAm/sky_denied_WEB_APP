import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-homepage',
  imports: [RouterModule],
  templateUrl: './homepage.component.html',
  styleUrl: './homepage.component.css'
})
export class HomepageComponent {
  activeTab: string = 'have-flight'; // Set the initial active tab

  switchTab(tabId: string) {
    this.activeTab = tabId;
  }
}
