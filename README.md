# PredayBackend

Backend API for **PreDay**, a personal productivity/task management project built with Flask and SQLite.

## Features

* User Registration & Login
* Secure Password Hashing using SHA-256
* User-specific Task Tables
* Add / Fetch / Delete Tasks
* Token-Protected Admin Route
* CORS Support for Frontend Integration
* SQLite Database Storage

---

## Tech Stack

* **Python**
* **Flask**
* **SQLite**
* **Flask-CORS**
* **python-dotenv**

---

## Project Structure

```bash
PredayBackend/
│
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile            # Deployment config
└── preday.db           # SQLite database (auto-generated)
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/tejashhxd/PredayBackend.git
cd PredayBackend
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the root directory:

```env
API_TOKEN=your_secret_api_token
FRONTEND_URL=http://localhost:3000
```

> Multiple frontend URLs can be comma-separated.

---

## Run the Server

```bash
python app.py
```

Server will start at:

```bash
http://127.0.0.1:5000
```

---

## API Endpoints

### Health Check

#### `GET /`

Returns server status message.

---

### Initialize Database

#### `GET /innit`

Creates the users table if it doesn't exist.

---

### Register User

#### `POST /register`

```json
{
  "username": "john",
  "password": "123456"
}
```

---

### Login User

#### `POST /login`

```json
{
  "username": "john",
  "password": "123456"
}
```

---

### Get All Users (Protected)

#### `GET /users`

Requires Header:

```http
Authorization: Bearer YOUR_API_TOKEN
```

---

### Get Tasks

#### `GET /task?username=john`

---

### Add Task

#### `POST /task`

```json
{
  "username": "john",
  "task": "Finish project"
}
```

---

### Delete Task

#### `DELETE /task`

```json
{
  "username": "john",
  "id": 1
}
```

---

## Security Notes

* Passwords are hashed with **SHA-256** before storage.
* Protected routes use Bearer Token Authentication.
* CORS restricted to allowed frontend origins.

---

## Future Improvements

* JWT Authentication
* Better Password Hashing with bcrypt
* Task Due Dates / Categories
* Update/Edit Task Endpoint
* SQL Injection Hardening for Dynamic Table Names
* Docker Deployment

---

## Author

Built by **Tejash**
GitHub: https://github.com/tejashhxd
