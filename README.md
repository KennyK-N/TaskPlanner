# AI Schedule Planner

A Flask web app that uses Google Gemini to automatically generate a daily schedule from a list of tasks, then pushes the result directly to Google Calendar.

---

## Features

- **Google OAuth login** — sign in securely with your Google account
- **AI-generated schedules** — enter up to 5 tasks and let Gemini assign time slots, descriptions, and structure your day
- **Location-aware** — optionally detect your location to give Gemini regional context when building your schedule
- **Review before committing** — preview and edit the generated schedule before it gets saved
- **Google Calendar integration** — confirmed schedules are created as real events on your Google Calendar
- **Schedule history** — past schedules are saved to a database and browsable from the home page with infinite scrolling
- **Reschedule** — re-send any past schedule to Google Calendar on a new date
- **Delete** — remove schedules you no longer need

---

## Tech Stack

| Layer            | Technology                                |
| ---------------- | ----------------------------------------- |
| Backend          | Python, Flask                             |
| AI               | Google Gemini (`google-genai`)            |
| Auth             | Google OAuth 2.0 (`google-auth-oauthlib`) |
| Calendar         | Google Calendar API                       |
| Database         | PostgreSQL + SQLAlchemy                   |
| Cache            | Redis                                     |
| Geocoding        | `geopy`, `geocoder`                       |
| Sanitization     | `bleach`                                  |
| Containerization | Docker, Docker Compose                    |

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- A [Google Cloud project](https://console.cloud.google.com/) with the following enabled:
  - Google Calendar API
  - OAuth 2.0 credentials (Web application)
- A [Gemini API key](https://aistudio.google.com/)

---

### 1. Clone the repo

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Set up your environment

Copy the sample env file and fill in your values:

```bash
cp .env.sample .env
```

---

### 3. Configure Google OAuth

In your [Google Cloud Console](https://console.cloud.google.com/):

1. Go to **APIs & Services → Credentials**
2. Create an **OAuth 2.0 Client ID** (Web application)
3. Add `http://localhost:5000/oauth2callback` as an authorised redirect URI
4. Make sure `CLIENT_ID`, `PROJECT_ID`, and `CLIENT_SECRET` in your `.env` match the corresponding credentials

---

### 4. Run with Docker Compose

```bash
docker compose up --build
```

The app will be available at **http://localhost:5000**

---

### 5. Running tests

```bash
# run pytest from the root directory
pytest
```

---

## How It Works

```
1. Log in with Google
        ↓
2. Enter up to 5 tasks, a date, a schedule name, and optionally share your location
        ↓
3. Gemini generates a full schedule with time slots and descriptions
        ↓
4. Review and edit the generated schedule
        ↓
5. Confirm → saved to PostgreSQL + pushed to Google Calendar
        ↓
6. View past schedules on the home page
   → Reschedule to a new date, or delete
```

---

## Project Structure

```
app/
├── api/                  # API routes (prompt, task finalize, create event)
│   ├── Gemini/           # Gemini AI integration
│   ├── Geocoding/        # Location detection
│   └── Google_Calendar/  # Google Calendar API integration
├── auth/                 # Google OAuth login, callback, revoke
├── database/             # SQLAlchemy models, CRUD operations
├── Main/                 # Home page and main views
├── redis/                # Redis caching helpers
├── static/               # JS, CSS
├── templates/            # Jinja2 HTML templates
├── tests/
│   ├── functional_test/  # Route-level tests
│   └── unit_test/        # Unit tests for CRUD, API, Redis
└── util/                 # Shared utilities (permissions, sanitization, time conversion)
```

---
