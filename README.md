# Getting Started with Poshan

## Running the Server

In the project directory, you can run:

```bash
python app.py
```

Runs the app in the development mode.\
Open <http://localhost:5000> to view it in your browser.

## Missing Modules

Recommended to create virtual environment and install modules from requirements.txt using:

```bash
python -m virtualenv venv
venv/scripts/activate
pip install -r requirements.txt
```

## Default Login Credentials

```text
School Incharge
---------------
Username: school01@poshan.in
Password: pass 
```

```text
School Student
--------------
Username: student0101@poshan.in
Password: pass
```

```text
Health Officer
----------------------
Username: admin@poshan.in
Password: pass
```

## MongoDB Errors

You need MongoDB installed in your PC to fix this error. The app takes care of initialising a database with dummy values, once mongodb is installed.
