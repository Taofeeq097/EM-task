# Project README

## Overview
This application is designed for efficient employee and leave management. It provides features such as role-based access control, department management, leave request workflows, and more.

---

## Project Setup

### Prerequisites
1. **Python**: Ensure Python 3.8 or higher is installed.
2. **Django**: Install Django using pip.

```bash
pip install django
```
3. **Database**: Configure your database in the `.env` file (default: SQLite).

---

### Setup Instructions

1. Clone the repository:

```bash
git clone <repository_url>
cd <project_directory>
```

2. Install project dependencies:

```bash
pip install -r requirements.txt
```

3. Set up the environment variables:

Create a `.env` file in the root of the project and populate it with the following structure:

```env
SECRET_KEY=****
DEBUG=True

# CEO Details
CEO_PASSWORD=****
CEO_EMAIL=c******
CEO_FIRST_NAME=********
CEO_LAST_NAME=********
```

4. Run database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Seed roles, departments, and create the CEO user:

Run the setup command:

```bash
python manage.py setup
```

This command will:
- Seed predefined roles and departments.
- Create a CEO user who doubles as the superuser and admin. The CEO’s details are taken from the `.env` file.

6. Start the development server:

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`.

---

## Commands

### `python manage.py setup`
This custom management command seeds the database with initial data:
- **Roles**: Seeds predefined roles (e.g., CEO, Manager, Employee).
- **Departments**: Seeds department data.
- **CEO User**: Creates a CEO user with superuser privileges using details from the `.env` file.

---

## Features

### Role Management
- Assign roles to users (e.g., CEO, Manager, Employee).

### Department Management
- Manage organizational departments.

### Leave Management
- Employees can request leave.
- Requests follow an approval workflow based on reporting hierarchy.

### Admin Panel
- Admin users can manage roles, departments, and employees.

---

## Additional Notes

- Ensure the `.env` file is kept secure and is not added to version control.
- For production, set `DEBUG=False` in the `.env` file and configure the `ALLOWED_HOSTS` setting in `settings.py`.

---

## Troubleshooting


### Contact
For support, contact the development team at `support@yourdomain.com`.

