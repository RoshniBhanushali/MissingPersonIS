
### Prerequisites
- Python 3.x
- `pip` (Python package installer)

### Clone the Repository
```bash
git clone https://github.com/thegeek36/Missing-Person-Detection-System.git
cd Missing-Person-Detection-System
```

### Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # For Windows use: venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create a New Database
Delete the existing `db.sqlite3` file (if present):
```bash
rm db.sqlite3  # For Windows, use: del db.sqlite3
```

Create a new database:
```bash
python manage.py migrate
```

### Create Admin Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to set up your admin username, email, and password.

### Run the Server
```bash
python manage.py runserver
```


