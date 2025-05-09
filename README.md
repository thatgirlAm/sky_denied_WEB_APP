# Sky Denied's Web Application

This is Sky Denied's repository for the web application.

## Technology

The web application will be using the following frameworks and technologies:
- **Angular 18** for the front-end
- **Laravel 12** for the back-end
- **PostgreSQL** for the database

## Containerizing the Web Application

Both the frontend and the backend have been dockerized. There is a specific way of building the project to ensure reproducibility, as the team has containerized the web application using Docker.

### Prerequisites

Before proceeding, ensure that:

- Docker and Docker Compose are installed and running on your system.

## Setup the .env File

The first step to run the project is to set up the `.env` file. Follow these steps:

1. Access the `./back` folder.
2. Copy the content of the `.env.example` file.
3. Create a new file named `.env` in the same folder (`./back`).
4. Paste the copied content into the new `.env` file.

### Two Ways to Build the Project

There are two methods to build and run the project:

### 1. Running the Overall Container of the Project

If you want to run both the frontend and the backend in one go, you can use Docker Compose.

From the `sky_denied_WEB_APP` folder, run the following command:

```bash
docker-compose build
```

Once the build is complete, navigate to the frontend's local website:

```bash
http://localhost:8080
```

The application will be functional after this step.

### 2. Running Both Containers Separately

If the first method doesn't work (e.g., due to port conflicts), you can try running the frontend and backend containers separately.

#### Step 1: Running the Backend Container

Access the `./back` folder and build the backend container with the following commands:

```bash
cd ./back
docker build -t laravel-backend .
```

#### Step 2: Running the Frontend Container

Next, access the `./front` folder and build the frontend container:

```bash
cd ./front
docker build -t angular-frontend .
```

#### Backend Running Command

If you're running the backend container separately, you can use the following command:

```bash
docker run --rm -p 8000:8000 \
-e DB_CONNECTION=pgsql \
-e DB_HOST=es-us-2-sky-denied-v2.postgres.database.azure.com \
-e DB_PORT=5432 \
-e DB_DATABASE=postgres \
-e DB_USERNAME=amaellediop \
-e DB_PASSWORD='abcd1234!' \
-e DB_SSLMODE=require \
laravel-backend \
php artisan serve --host=0.0.0.0 --port=8000
```

## Accessing the Application

After running the containers, you can access the application in your browser:

- Frontend: http://localhost:8080
- Backend (API): http://localhost:8000

## Features Implemented

- **Header**: Fully functional.
- **Footer**: Partially functional.
- **Search Page**:
  - **Search Form**: Inputs are present, but no logic has been implemented yet.
  - **Search Results**: The design is complete, and you can trigger both popups (Request a Prediction and Get Notified), as well as close them. However, it uses dummy data, and no backend logic has been integrated. The "Check Prediction" button must also be updated when a prediction has already been triggered.
  - **Prediction Results**: The popup is nearly complete, missing compensation links and logic to display different colors on the prediction banner.
  - **Email Popup**: The popup is displayed, but no logic to save emails and flight numbers to the database has been implemented yet.
- **Responsiveness**: Some content is responsive, while other elements still need work. This issue is being addressed.

## Stopping the Containers

If you're running containers separately, you can stop them using the following commands:

For the backend:

```bash
docker stop laravel-backend
```

For the frontend:

```bash
docker stop angular-frontend
```

## Troubleshooting

### Port Already in Use

If you encounter port conflicts (e.g., port 8000 is already in use), you can modify the `-p` flag in the docker run command. For example, if 8000 is occupied, use port 8080:

```bash
-p 8080:8000
```

### Database Connection Issues

Ensure that your database server is running and accessible. Double-check the values in your `.env` file, especially `DB_HOST`, `DB_USERNAME`, and `DB_PASSWORD`.

### Missing .env File

If the `.env` file is not correctly set up, the application may not start. Make sure you've copied the contents of `.env.example` into a new `.env` file inside the `./back` folder.