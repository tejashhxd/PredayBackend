# PreDay Backend

The backend API for **PreDay**, a personal productivity and task-management application.

Built with **Flask**, **SQLAlchemy**, and **SQLite**, the backend provides user authentication, task management, protected API routes, and communication with the React frontend.

## Features

* User registration and login
* JWT-based authentication using HTTP-only cookies
* Protected API routes
* Password hashing
* Create, read, update, and delete tasks
* Task due dates
* User-specific task management
* CORS support
* SQLAlchemy ORM
* SQLite database
* Environment-variable based configuration
* Deployment-ready Flask application

## Tech Stack

| Technology         | Purpose                     |
| ------------------ | --------------------------- |
| Python             | Backend language            |
| Flask              | Web framework               |
| Flask-JWT-Extended | JWT authentication          |
| SQLAlchemy         | ORM and database management |
| SQLite             | Database                    |
| Flask-CORS         | Cross-origin requests       |
| python-dotenv      | Environment variables       |

## Project Structure

```text
PredayBackend/
│
├── app.py
├── models.py
├── requirements.txt
├── Procfile
├── .gitignore
├── .env
└── preday.db
```

### Main Files

**`app.py`**

Contains the Flask application, API routes, authentication logic, JWT configuration, CORS configuration, and task operations.

**`models.py`**

Contains the SQLAlchemy database models and relationships between users and tasks.

**`requirements.txt`**

Contains the Python dependencies required to run the application.

**`Procfile`**

Contains the deployment configuration for platforms such as Render.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tejashhxd/PredayBackend.git
cd PredayBackend
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory:

```env
JWT_SECRET_KEY=your_secret_key
FRONTEND_URL=http://localhost:3000
```

For production, use a strong randomly generated secret key.

Never commit your `.env` file to the repository.

## Running the Backend

Start the Flask development server:

```bash
python app.py
```

The API will be available at:

```text
http://127.0.0.1:5000
```

## Authentication

PreDay uses JWT-based authentication with HTTP-only cookies.

The authentication flow works approximately like this:

```text
React Frontend
      |
      | POST /login
      v
Flask Backend
      |
      | Validate credentials
      v
JWT generated
      |
      | HTTP-only cookie
      v
Browser
```

After authentication, the browser automatically sends the authentication cookie with subsequent requests to protected endpoints.

This prevents the frontend from having to manually store and attach the JWT to every request.

## API Endpoints

### Authentication

#### Register

```http
POST /register
```

Example request:

```json
{
  "username": "john",
  "password": "password123"
}
```

#### Login

```http
POST /login
```

Example request:

```json
{
  "username": "john",
  "password": "password123"
}
```

On successful authentication, the backend generates a JWT and stores it in an HTTP-only cookie.

#### Logout

```http
POST /logout
```

Clears the authentication cookie and logs the user out.

### User

#### Get Current User

```http
GET /me
```

Returns information about the currently authenticated user.

This endpoint requires a valid JWT cookie.

### Tasks

#### Get Tasks

```http
GET /tasks
```

Returns tasks belonging to the authenticated user.

#### Create Task

```http
POST /tasks
```

Example request:

```json
{
  "task": "Finish backend authentication",
  "due_date": "2026-08-25"
}
```

#### Update Task

```http
PUT /tasks/<task_id>
```

Example request:

```json
{
  "task": "Finish JWT implementation",
  "completed": true
}
```

#### Delete Task

```http
DELETE /tasks/<task_id>
```

Deletes the specified task belonging to the authenticated user.

## CORS and Cookies

Since the PreDay frontend and backend are deployed separately, cross-origin requests need to be configured correctly.

The backend uses Flask-CORS together with cookie-based JWT authentication.

For authenticated requests, the frontend needs to include credentials.

Using `fetch`:

```javascript
fetch("https://your-backend-url.com/tasks", {
  credentials: "include"
});
```

Using Axios:

```javascript
axios.get("https://your-backend-url.com/tasks", {
  withCredentials: true
});
```

The backend must also allow credentials for the configured frontend origin.

For production deployments, cookie settings such as `Secure` and `SameSite` should be configured appropriately for the deployment environment.

## Database

PreDay currently uses **SQLite** with **SQLAlchemy** as the ORM.

The database stores users and their associated tasks.

The relationship can be represented as:

```text
User
 |
 +-- Task
 +-- Task
 +-- Task
```

Each task belongs to a specific user.

## Security

The backend implements several security measures:

* Password hashing before storing passwords
* JWT-based authentication
* HTTP-only authentication cookies
* Protected API routes
* CORS restrictions
* Environment variables for sensitive configuration
* User-specific task authorization

Sensitive credentials and secret keys should never be committed to the repository.

## Deployment

The backend can be deployed using services such as Render.

Typical deployment configuration:

```text
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app
```

Production environment variables should be configured through the hosting provider instead of being committed to the repository.

## Frontend

The PreDay frontend is built with React.

The frontend communicates with this Flask API for:

* User authentication
* Session management
* Task creation
* Task retrieval
* Task updates
* Task deletion

## What I Learned

Building PreDay helped me understand and implement:

* REST API development with Flask
* Authentication and authorization
* JWT and cookie-based authentication
* CORS and cross-origin requests
* SQLAlchemy ORM
* Relational database design
* Environment variables
* Frontend-backend communication
* API deployment
* Production authentication considerations


## Author

**Tejash**

GitHub: [@tejashhxd](https://github.com/tejashhxd)

## License

This project is open source and available under the MIT License.
