<div align="center">

# G-SMARTCLASS

**A modular school and learning application project.**

A Python desktop codebase integrating Firebase services and AI-oriented feature modules.

</div>

---

## Overview

G-SmartClass is an education-technology project organized around a modular desktop application. Its source tree contains authentication, academic, administration, analytics, and AI-related feature areas, with Firebase REST integration configured for application services.

The repository is still in development. Its module structure is broader than the current desktop bootstrap: the current entry flow registers authentication screens, while the dashboard is explicitly a placeholder. A directory existing in the repository should not be interpreted as proof that the corresponding user workflow is complete.

## Source areas

| Area | Source modules |
| --- | --- |
| Authentication | Splash, login, registration, password recovery, email verification, device pairing |
| Academic | Assignments, attendance, certificates, courses, gradebook, materials, quizzes |
| AI-oriented modules | Flashcards, quiz generation, study plans, summaries, translation, tutoring |
| Administration | Administrative feature modules |
| Analytics | Analytics feature module |
| Platform integration | Firebase REST services, environment configuration, task runner, Qt resources |

## Technology

- Python
- PySide6
- Firebase Authentication and Firestore REST APIs
- Firebase Realtime Database REST API
- Requests and python-dotenv
- Cryptography, Pillow, and QR code utilities
- Gemini API configuration for AI-related integrations
- Qt Style Sheets

## Requirements

- Python 3.10 or newer is recommended for the development environment.
- Packages listed in desktop/requirements.txt.
- A Firebase project with the required Authentication and database services enabled.
- A Gemini API key only when exercising AI-related integrations.

## Local setup

    git clone https://github.com/gusti111/G-SmartClass.git
    cd G-SmartClass

    python -m venv .venv

Windows:

    .venv\Scripts\activate

macOS / Linux:

    source .venv/bin/activate

Install dependencies:

    python -m pip install --upgrade pip
    pip install -r desktop/requirements.txt

Create a local environment file:

    # Windows PowerShell
    Copy-Item .env.example .env

    # macOS / Linux
    cp .env.example .env

Configure the Firebase project values in .env. Add the Gemini API key only if the corresponding integration is being tested. Keep real credentials out of Git.

The current desktop bootstrap exposes run_application() but does not define a direct module launcher. From the repository root, the bootstrap can be invoked with:

    python -c "from desktop.app import run_application; raise SystemExit(run_application())"

This launches the current authentication-oriented desktop shell; the dashboard remains a placeholder in the inspected source.

## Architecture

    desktop/
    ├── config/          # Environment, Firebase, and application settings
    ├── core/            # Shared UI and task infrastructure
    ├── features/
    │   ├── authentication/
    │   ├── academic/
    │   ├── admin/
    │   ├── ai/
    │   └── analytics/
    ├── routes/          # View routing
    └── themes/          # Qt styles

Firebase access is implemented through REST endpoints using ordinary HTTP requests. The source does not require Firebase Admin SDK or Pyrebase in the desktop client.

## Configuration and security

- Use a dedicated Firebase development project.
- Restrict Firebase API keys according to the services and platforms that need them.
- Configure database security rules before using real student or school data.
- Never commit .env, service-account JSON files, or private AI credentials.
- Treat client-side configuration as public application configuration, not as a substitute for backend authorization.

## Current limitations

- The desktop dashboard is still a placeholder in the bootstrap.
- Feature folders represent project modules; each screen and workflow still requires integration and end-to-end validation.
- The backend/functions source directory is present, but its current index.ts file is empty. Do not assume a deployed Cloud Functions backend is included.
- No complete automated test or release workflow is documented in the current root source tree.

## Project status

An in-progress modular application project. Validate authentication, data authorization, AI integrations, and each academic workflow against a configured development environment before presenting the application as production-ready.

## Author

**Gusty Faqikh** · [GitHub](https://github.com/gusti111)