# Word Guess Game




https://github.com/user-attachments/assets/f6edfcb8-b666-4ad9-aa9e-e77eccd222a6



### Word Guess Game

A browser-based word-guessing game built with Python and Flask. This project challenges users to guess a five-letter word with limited attempts, providing color-coded feedback on each guess. It features user authentication, daily game limits, and an administrative dashboard for viewing game statistics and user-specific reports.

-----

### Features

  * **User Authentication**: Users can register and log in to track their personal game history and progress.
  * **Daily Game Limit**: A maximum of three games can be played per day to encourage users to return.
  * **Intelligent Feedback**: Guesses are evaluated with a color-coded system:
      * **Green**: Correct letter in the correct position.
      * **Orange**: Correct letter in the wrong position.
      * **Gray**: Letter is not in the word.
  * **Admin Dashboard**: Administrators can access a dedicated page to view comprehensive reports, including daily summaries and detailed user game histories.
  * **Responsive Design**: The game is optimized for a seamless experience on both desktop and mobile devices.

-----

### Technologies Used

  * **Backend**: Python
  * **Web Framework**: Flask
  * **Database**: SQLite (managed with Flask-SQLAlchemy)
  * **Forms**: Flask-WTF
  * **User Management**: Flask-Login
  * **Security**: Werkzeug (for password hashing)
  * **Frontend**: HTML, CSS, JavaScript

-----

### Setup and Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/Priya1509/Word-Guess.git
    cd Word-Guess
    ```

2.  **Create a virtual environment** (recommended):

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:

      * **Windows**: `venv\Scripts\activate`
4.  **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the application**:

    ```bash
    python app.py
    ```

6.  **Access the game**: Open your web browser and navigate to `http://127.0.0.1:5000`.

-----

### Usage

**1. Registration & Login**

  - Navigate to the Register page and create a new account. The system enforces validation rules for usernames and passwords.
  - Once registered, you can log in with your new credentials. After logging in, you will be redirected to the game page.

**2. Playing the Game**

  - On the game page, enter a 5-letter word in the input field and click "Guess."
  - The game board will update to show your guess with color-coded feedback.
  - Your progress, including guesses made and remaining attempts, is displayed.

**3. Admin Reports**

  - To access the admin features, you must log in with an administrator account.
  - After logging in as an admin, the navigation will automatically show a link to "Admin Reports."
  - The admin dashboard allows you to view reports for a specific date or for individual users by selecting them from a dropdown menu.

-----

### File Structure

```
Word-Guess/
├── app.py                # Main Flask application file
├── requirements.txt      # Python dependencies
├── instance/
│   └── guessword.db      # SQLite database file
└── templates/
    ├── base.html         # Base template for all pages
    ├── index.html        # Landing page
    ├── login.html        # Login form
    ├── register.html     # Registration form
    ├── play.html         # The main game page
    ├── admin_reports.html # Admin dashboard page
    └── pdf_report.html   # Daily and user report page
```
