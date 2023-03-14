# Getting Started with Poshan

## Running the Server

In the project directory, you can run:

```bash
python app.py
```

Runs the app in the development mode.\
Open <http://localhost:5000> to view it in your browser.

![image](https://user-images.githubusercontent.com/73932121/224907918-18fd1a78-eb6e-4cd0-a03d-f7354030fa7b.png)

## Missing Modules

Recommended to create virtual environment and install modules from requirements.txt using:

```bash
python -m virtualenv venv
venv/scripts/activate
pip install -r requirements.txt
```

## Sample Login Credentials

Check out the credentials available in [authdata.py](./authdata.py). Below are some sample creds

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
School Parent
-------------
Username: parent0101@poshan.in
Password: pass 
```

```text
Health Officer
----------------------
Username: admin@poshan.in
Password: pass
```

![image](https://user-images.githubusercontent.com/73932121/224907730-f9502952-85a5-4555-92f6-fa31cb58b603.png)

## MongoDB Errors

You need MongoDB installed in your PC to fix this error. The app takes care of initialising a database with dummy values, once mongodb is installed.
