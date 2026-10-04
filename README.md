# FinPilot AI

AI-powered personal finance management and Money Coach application built with Flask and Gemini.

FinPilot AI helps users track income, expenses, budgets, savings and financial goals, then turns that data into practical guidance through a Gemini-powered AI Money Coach.

## Features

- User registration and login
- Personal finance dashboard
- Income tracking
- Expense tracking
- Budget management
- Savings tracking
- Financial goals
- Analytics
- AI Money Coach powered by Gemini
- Chat/feedback functionality

## Tech Stack

- Python
- Flask
- SQLite
- Flask-WTF
- Google Gemini API
- HTML/CSS/JavaScript

## Project Structure

```
routes/       Flask blueprints: authentication, dashboard, income, expenses,
              budget, goals, analytics and the AI Money Coach endpoints
models/       SQLAlchemy models (User, Income, Expense, Goal, Chat)
forms/        WTForms definitions used for validation
utils/        Gemini integration, Money Coach logic, insights and helpers
templates/    Jinja2 HTML templates
static/       CSS and JavaScript assets
migrations/   One-time database migration scripts
```

## Setup

Create a virtual environment:

```
python -m venv venv
```

Activate it (Windows):

```
venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

## Environment Variables

FinPilot AI reads its configuration from environment variables. Create a
`.env` file in the project root and set the following variable names:

| Variable | Required | Purpose |
|---|---|---|
| `FINPILOT_SECRET_KEY` | Yes | Flask session signing key |
| `GEMINI_API_KEY` | Yes | Google Gemini API access |
| `FINPILOT_DATABASE_URI` | No | Override the default SQLite location |
| `FINPILOT_COOKIE_SECURE` | No | Set to `1` to enable secure cookies over HTTPS |

Secrets should be stored in `.env` and **never committed** to the repository.

## Run

```
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

## Database

The local SQLite database is stored at:

```
instance/finpilot.db
```

It is created automatically on first run and is intentionally excluded from
Git via `.gitignore`, so it will never be committed or uploaded.

## Security Notes

- Never commit `.env` or any file containing credentials
- Never expose API keys or secret keys in source code
- Passwords are hashed using Werkzeug; plaintext passwords are never stored
- CSRF protection is enabled application-wide via Flask-WTF

## Current Status

FinPilot AI includes a working dashboard, financial tracking (income,
expenses, budget, savings and goals), analytics, and a Gemini-powered AI
Money Coach that answers questions using the signed-in user's own financial
data.

## License

This project is provided for educational and personal use.
