# GrowVeggies Dashboard

The GrowVeggies Dashboard is for students of HomesteadTO to use as a resource for farming and gardening at home. It makes the course textbook available in a searchable format.

This is a simple dashboard web application built with Flask and HTMX for managing and searching content from a PDF database. The app includes user authentication via PocketBase, allowing users to register, log in, and search for content in a SQLite database.

## Features
- User registration and authentication using PocketBase
- Search functionality with filters by section
- Dynamic updates using HTMX

## Project Structure
- `app/`: Contains the main application files.
  - `app.py`: The main Flask application.
  - `requirements.txt`: List of dependencies for the project.
  - `templates/`: Contains HTML templates for the application.
  - `pocketbase/`: Contains PocketBase setup files.

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- PocketBase (downloaded and set up)

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd GrowVeggiesQA
   ```
2. Install the required dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```
3. Set up PocketBase:
   - Download PocketBase and place it in the `app/pocketbase/` directory.
   - Create the `pb_schema.json` file in the same directory to define your user collection.
   - Start PocketBase with the command:
     ```bash
     cd app/pocketbase
     ./start_pocketbase.sh
     ```

## Running the Application
1. Start the Flask application:
   ```bash
   cd app
   python app.py
   ```
2. Access the application in your web browser at `http://127.0.0.1:5000`.
3. Access the PocketBase admin interface at `http://127.0.0.1:8090` to manage users.

## Usage
- Users can register through the registration page.
- After registration, users can log in with their credentials.
- The dashboard allows users to search for content from the PDF database, filtered by section.