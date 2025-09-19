/*document.addEventListener('DOMContentLoaded', function() {
    // Correctly reference the input and button elements based on play.html
    const guessInput = document.getElementById('word-input');
    const submitBtn = document.getElementById('submit-guess');
    const messageArea = document.getElementById('message-area');
    const guessesRemainingSpan = document.getElementById('guesses-remaining');
    const gameBoard = document.getElementById('game-board');

    // Get game data from the JSON script tag in play.html
    const gameData = JSON.parse(document.getElementById('game-data').textContent);
    let gameSessionId = gameData.gameSessionId;
    let isGameOver = gameData.gameOver;

    // A function to disable input and buttons when the game is over
    const disableGame = () => {
        guessInput.disabled = true;
        submitBtn.disabled = true;
    };

    // If the game is already over when the page loads, disable the inputs
    if (isGameOver) {
        disableGame();
        return;
    }

    // Event listener for the "Guess" button
    submitBtn.addEventListener('click', () => {
        const guessedWord = guessInput.value.trim().toUpperCase();

        // Basic validation before sending to the server
        if (guessedWord.length !== 5 || !/^[A-Z]{5}$/.test(guessedWord)) {
            messageArea.textContent = "Please enter a 5-letter English word.";
            return;
        }

        // Send the guess to the back-end's /guess API
        fetch('/guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_session_id: gameSessionId,
                word: guessedWord
            })
        })
        .then(response => {
            if (!response.ok) {
                // If the response is not ok (e.g., 400 or 500), parse the error message
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Something went wrong.');
                });
            }
            return response.json();
        })
        .then(data => {
            // The server response contains the feedback and updated game state
            updateGameBoard(data.guessed_word, data.feedback);
            guessesRemainingSpan.textContent = 5 - data.guesses_made;
            messageArea.textContent = data.message || '';

            if (data.game_over) {
                disableGame();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageArea.textContent = error.message || 'An error occurred. Please try again.';
        });

        // Clear the input field for the next guess
        guessInput.value = '';
    });

    // Function to visually update the game board with the new guess
    const updateGameBoard = (word, feedback) => {
        // Find the first empty row on the board
        // The game board is built in play.html, so we just need to find the correct row
        const guessRows = document.querySelectorAll('.guess-row');
        for (let i = 0; i < guessRows.length; i++) {
            const row = guessRows[i];
            // Check if the row is for the current guess being made
            if (row.querySelectorAll('.letter-box:not([class*="green"]):not([class*="orange"]):not([class*="grey"])').length === 5) {
                // Fill the empty row with the new guess and its feedback
                const letterBoxes = row.querySelectorAll('.letter-box');
                for (let j = 0; j < 5; j++) {
                    letterBoxes[j].textContent = word[j];
                    letterBoxes[j].classList.add(feedback[j]);
                }
                break;
            }
        }
    };

    function showConfetti() {
        const confettiContainer = document.createElement('div');
        confettiContainer.style.position = 'fixed';
        confettiContainer.style.top = '0';
        confettiContainer.style.left = '0';
        confettiContainer.style.width = '100%';
        confettiContainer.style.height = '100%';
        confettiContainer.style.pointerEvents = 'none';
        confettiContainer.style.zIndex = '9999';
        document.body.appendChild(confettiContainer);
        
        for (let i = 0; i < 100; i++) {
            const confetti = document.createElement('div');
            confetti.style.position = 'absolute';
            confetti.style.width = '10px';
            confetti.style.height = '10px';
            confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
            confetti.style.borderRadius = '50%';
            confetti.style.top = '0';
            confetti.style.left = `${Math.random() * 100}%`;
            confetti.style.animation = `confetti-fall ${1 + Math.random() * 2}s forwards`;
            confettiContainer.appendChild(confetti);
        }
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes confetti-fall {
                0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        setTimeout(() => {
            if (confettiContainer.parentNode) {
                confettiContainer.parentNode.removeChild(confettiContainer);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 3000);
    }

});
*/


document.addEventListener('DOMContentLoaded', function() {
    const guessInput = document.getElementById('word-input');
    const submitBtn = document.getElementById('submit-guess');
    const messageArea = document.getElementById('message-area');
    const guessesRemainingSpan = document.getElementById('guesses-remaining');
    const gameBoard = document.getElementById('game-board');

    const gameData = JSON.parse(document.getElementById('game-data').textContent);
    let gameSessionId = gameData.gameSessionId;
    let isGameOver = gameData.gameOver;

    const disableGame = () => {
        guessInput.disabled = true;
        submitBtn.disabled = true;
    };

    if (isGameOver) {
        disableGame();
        return;
    }

    submitBtn.addEventListener('click', () => {
        const guessedWord = guessInput.value.trim().toUpperCase();

        if (guessedWord.length !== 5 || !/^[A-Z]{5}$/.test(guessedWord)) {
            messageArea.textContent = "Please enter a 5-letter English word.";
            return;
        }

        fetch('/guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_session_id: gameSessionId,
                word: guessedWord
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Something went wrong.');
                });
            }
            return response.json();
        })
        .then(data => {
    updateGameBoard(data.guessed_word, data.feedback);
    guessesRemainingSpan.textContent = 5 - data.guesses_made;

    // Show the message
    messageArea.textContent = data.message || '';
    messageArea.className = "game-message"; // reset class
    if (data.status === 'won') {
        messageArea.classList.add("success");
        showConfetti();
    } else if (data.status === 'lost') {
        messageArea.classList.add("error");
        showErrorParticles();
    }

    if (data.game_over) {
        disableGame();
    }
});

        guessInput.value = '';
    });

    const updateGameBoard = (word, feedback) => {
        const guessRows = document.querySelectorAll('.guess-row');
        for (let i = 0; i < guessRows.length; i++) {
            const row = guessRows[i];
            if (row.querySelectorAll('.letter-box:not([class*="green"]):not([class*="orange"]):not([class*="grey"])').length === 5) {
                const letterBoxes = row.querySelectorAll('.letter-box');
                for (let j = 0; j < 5; j++) {
                    letterBoxes[j].textContent = word[j];
                    letterBoxes[j].classList.add(feedback[j]);
                }
                break;
            }
        }
    };

    function showConfetti() {
        const confettiContainer = document.createElement('div');
        confettiContainer.style.position = 'fixed';
        confettiContainer.style.top = '0';
        confettiContainer.style.left = '0';
        confettiContainer.style.width = '100%';
        confettiContainer.style.height = '100%';
        confettiContainer.style.pointerEvents = 'none';
        confettiContainer.style.zIndex = '9999';
        document.body.appendChild(confettiContainer);
        
        for (let i = 0; i < 100; i++) {
            const confetti = document.createElement('div');
            confetti.style.position = 'absolute';
            confetti.style.width = '10px';
            confetti.style.height = '10px';
            confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
            confetti.style.borderRadius = '50%';
            confetti.style.top = '0';
            confetti.style.left = `${Math.random() * 100}%`;
            confetti.style.animation = `confetti-fall ${1 + Math.random() * 2}s forwards`;
            confettiContainer.appendChild(confetti);
        }
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes confetti-fall {
                0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        setTimeout(() => {
            if (confettiContainer.parentNode) {
                confettiContainer.parentNode.removeChild(confettiContainer);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 3000);
    }

    // The new showErrorParticles function to display on a loss
    function showErrorParticles() {
        const errorContainer = document.createElement('div');
        errorContainer.style.position = 'fixed';
        errorContainer.style.top = '0';
        errorContainer.style.left = '0';
        errorContainer.style.width = '100%';
        errorContainer.style.height = '100%';
        errorContainer.style.pointerEvents = 'none';
        errorContainer.style.zIndex = '9999';
        document.body.appendChild(errorContainer);

        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.style.position = 'absolute';
            particle.style.fontSize = '50px';
            particle.style.opacity = '0';
            particle.textContent = '😔';
            
            particle.style.top = '0';
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.animation = `sad-fall ${2 + Math.random() * 2}s forwards`;
            errorContainer.appendChild(particle);
        }
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes sad-fall {
                0% { transform: translateY(0) scale(1); opacity: 1; }
                100% { transform: translateY(100vh) scale(0.5); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        setTimeout(() => {
            if (errorContainer.parentNode) {
                errorContainer.parentNode.removeChild(errorContainer);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 2000);
    }
});