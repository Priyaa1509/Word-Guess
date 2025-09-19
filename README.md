# Word Guess Game

1. Create virtualenv & install:
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt

2. Initialize DB (creates guessword.db & seed words & admin user):
   python init_db.py

3. Run the app:
   python app.py
   -> open http://127.0.0.1:5000

Admin account (created by init_db.py):
  username: admin
  password: Admin@123
Notes:
- Each user can try up to 3 different words per day.
- Each word gives max 5 guesses.
- Password rules: at least 5 chars, include a digit and one of $ % * @.
- Username rules: at least 5 letters, include both upper and lower-case letters, letters only.
#

