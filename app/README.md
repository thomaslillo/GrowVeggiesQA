# App Overview

This application is built using **Flask** and **PocketBase**. Below is an explanation of each technology and its role in the project.

## Flask

Flask is a lightweight WSGI web application framework in Python. It is designed with simplicity and flexibility in mind, making it easy to get started with web development. Flask provides tools, libraries, and technologies that allow you to build a web application quickly and efficiently. 

### Key Features of Flask:
- **Lightweight and Modular**: Flask is minimalistic and allows you to add extensions as needed.
- **Built-in Development Server**: Flask comes with a built-in server for testing and debugging.
- **RESTful Request Dispatching**: Flask makes it easy to create RESTful APIs.

## PocketBase

PocketBase is a lightweight backend solution that provides a real-time database, authentication, and file storage. It allows developers to build applications without managing a server. PocketBase is designed to be easy to use and integrates well with various frontend frameworks.

### Key Features of PocketBase:
- **Real-time Database**: PocketBase offers a real-time database that allows for instant data synchronization.
- **User Authentication**: It provides built-in user authentication features.
- **File Storage**: PocketBase allows you to store files easily.

## Running the Application

### Running Flask
To run the Flask application, follow these steps:
1. Navigate to the `app` directory:
   ```bash
   cd app
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set the environment variable for Flask:
   ```bash
   export FLASK_APP=your_flask_app.py
   ```
4. Run the Flask application:
   ```bash
   flask run
   ```

### Running PocketBase
To start PocketBase, execute the following command:
```bash
./start_pocketbase.sh
```

Make sure that the `start_pocketbase.sh` script has execution permissions. You can set this by running:
```bash
chmod +x start_pocketbase.sh
```
