# Word Guess Game




https://github.com/user-attachments/assets/f6edfcb8-b666-4ad9-aa9e-e77eccd222a6



Notes:
- Each user can try up to 3 different words per day.
- Each word gives max 5 guesses.
- Password rules: at least 5 chars, include a digit and one of $ % * @.
- Username rules: at least 5 letters, include both upper and lower-case letters, letters only.
- Admin should be able to generate Daily report and User Specific report

1. Create virtualenv & install:
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt

2. Initialize DB (creates guessword.db & seed words & admin user):
   python init_db.py

3. Run the app:
   python app.py

#


