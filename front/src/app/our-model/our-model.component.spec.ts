import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OurModelComponent } from './our-model.component';

describe('OurModelComponent', () => {
  let component: OurModelComponent;
  let fixture: ComponentFixture<OurModelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OurModelComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OurModelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
