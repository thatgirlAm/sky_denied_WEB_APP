# Sky Denied's Web Application
This is Sky Denied's repository for the web application.

# Technology
The web application will be using the following frameworks and tehcnology : 
- Angular 18 for the front-end
- Laravel 12 for the back-end 
- PostGre for the Database

# Containerizing the web application

Both the frontend and the backend have been dockerized and there is a peculiar way of building the whole project because 

# What have been made?
- Header: entirely functional
- Footer: almost entirely functional, TODO: add links for terms of use and privacy policy
- Search page:
  - Search form: the input are here, but no logic have been implemented
  - Search results: the design is good, you can trigger both pop up (request a prediction and get notified) and 
close them as you want. However, this is dummy data, not the real one, and no logic triggering the backend
have been implemented. The button check prediction must be updated as well when a prediction has already been triggered
before
  - Prediction results: the pop-up is almost done, it lacks the compensation links and the logic to display one
color or the other on the prediction banner. 
  - Email pop up: the display is here, but no logic that save email and flight number into database have been
implemented.
- Some content is responsive, other is not, this issue is being taking care of. 
