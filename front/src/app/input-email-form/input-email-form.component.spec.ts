import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InputEmailFormComponent } from './input-email-form.component';

describe('InputEmailFormComponent', () => {
  let component: InputEmailFormComponent;
  let fixture: ComponentFixture<InputEmailFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InputEmailFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InputEmailFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
