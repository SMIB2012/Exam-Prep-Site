// Quiz JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize quiz functionality
    initQuizInterface();
    initQuestionNavigation();
    initTimerFunctionality();
    initAnswerSelection();
    initAutoSave();
    initKeyboardShortcuts();
});

// Initialize quiz interface
function initQuizInterface() {
    const quizContainer = document.querySelector('.quiz-container');
    if (!quizContainer) return;
    
    // Add smooth transitions
    quizContainer.style.opacity = '0';
    setTimeout(() => {
        quizContainer.style.transition = 'opacity 0.5s ease';
        quizContainer.style.opacity = '1';
    }, 100);
    
    // Initialize progress bar
    updateProgressBar();
    
    // Initialize question counter
    updateQuestionCounter();
}

// Initialize question navigation
function initQuestionNavigation() {
    const prevBtn = document.getElementById('prev-question');
    const nextBtn = document.getElementById('next-question');
    const questionNumbers = document.querySelectorAll('.question-number');
    
    // Previous/Next button handlers
    if (prevBtn) {
        prevBtn.addEventListener('click', () => navigateQuestion(-1));
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => navigateQuestion(1));
    }
    
    // Question number navigation
    questionNumbers.forEach(numberBtn => {
        numberBtn.addEventListener('click', function() {
            const questionIndex = parseInt(this.getAttribute('data-question-index'));
            navigateToQuestion(questionIndex);
        });
    });
}

// Initialize timer functionality
function initTimerFunctionality() {
    const timerElement = document.getElementById('quiz-timer');
    if (!timerElement) return;
    
    const duration = parseInt(timerElement.getAttribute('data-duration'));
    if (!duration) return;
    
    startQuizTimer(timerElement, duration);
}

// Start quiz timer
function startQuizTimer(element, totalSeconds) {
    const warningThreshold = 300; // 5 minutes
    const criticalThreshold = 60; // 1 minute
    
    function updateTimer() {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        const timeString = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        element.textContent = timeString;
        
        // Apply warning styles
        element.classList.remove('timer-warning', 'timer-critical');
        if (totalSeconds <= criticalThreshold) {
            element.classList.add('timer-critical');
        } else if (totalSeconds <= warningThreshold) {
            element.classList.add('timer-warning');
        }
        
        // Auto-submit when time runs out
        if (totalSeconds <= 0) {
            clearInterval(timerInterval);
            autoSubmitQuiz();
            return;
        }
        
        totalSeconds--;
    }
    
    updateTimer(); // Initial call
    const timerInterval = setInterval(updateTimer, 1000);
    
    // Store timer in session storage
    sessionStorage.setItem('quizTimerInterval', timerInterval);
}

// Initialize answer selection
function initAnswerSelection() {
    const answerOptions = document.querySelectorAll('.answer-option');
    
    answerOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from siblings
            const siblings = this.parentNode.querySelectorAll('.answer-option');
            siblings.forEach(sibling => sibling.classList.remove('selected'));
            
            // Add selected class to current option
            this.classList.add('selected');
            
            // Update question status
            markQuestionAnswered();
            
            // Auto-save answer
            saveCurrentAnswer();
            
            // Update progress
            updateProgressBar();
        });
        
        // Add hover effects
        option.addEventListener('mouseenter', function() {
            if (!this.classList.contains('selected')) {
                this.style.backgroundColor = 'rgba(13, 110, 253, 0.05)';
            }
        });
        
        option.addEventListener('mouseleave', function() {
            if (!this.classList.contains('selected')) {
                this.style.backgroundColor = '';
            }
        });
    });
}

// Initialize auto-save functionality
function initAutoSave() {
    let autoSaveInterval;
    
    // Auto-save every 30 seconds
    autoSaveInterval = setInterval(() => {
        saveQuizProgress();
    }, 30000);
    
    // Save on page unload
    window.addEventListener('beforeunload', function(e) {
        saveQuizProgress();
        
        // Show warning if quiz is not submitted
        const isSubmitted = sessionStorage.getItem('quizSubmitted');
        if (!isSubmitted) {
            e.preventDefault();
            e.returnValue = 'Your quiz progress will be lost. Are you sure you want to leave?';
        }
    });
}

// Initialize keyboard shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only handle shortcuts when not typing in input fields
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        switch(e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                navigateQuestion(-1);
                break;
            case 'ArrowRight':
                e.preventDefault();
                navigateQuestion(1);
                break;
            case '1':
            case '2':
            case '3':
            case '4':
                e.preventDefault();
                selectAnswer(parseInt(e.key) - 1);
                break;
            case 'Enter':
                e.preventDefault();
                if (e.ctrlKey) {
                    submitQuiz();
                }
                break;
        }
    });
}

// Navigate to previous/next question
function navigateQuestion(direction) {
    const currentIndex = getCurrentQuestionIndex();
    const totalQuestions = getTotalQuestions();
    
    let newIndex = currentIndex + direction;
    
    // Boundary checks
    if (newIndex < 0) newIndex = 0;
    if (newIndex >= totalQuestions) newIndex = totalQuestions - 1;
    
    navigateToQuestion(newIndex);
}

// Navigate to specific question
function navigateToQuestion(index) {
    // Save current answer before navigating
    saveCurrentAnswer();
    
    // Hide current question
    const currentQuestion = document.querySelector('.question-container.active');
    if (currentQuestion) {
        currentQuestion.classList.remove('active');
        currentQuestion.style.opacity = '0';
    }
    
    // Show target question with animation
    setTimeout(() => {
        const targetQuestion = document.querySelector(`[data-question-index="${index}"]`);
        if (targetQuestion) {
            targetQuestion.classList.add('active');
            targetQuestion.style.opacity = '1';
        }
        
        // Update UI elements
        updateQuestionCounter();
        updateProgressBar();
        updateNavigationButtons();
    }, 150);
}

// Select answer by index
function selectAnswer(answerIndex) {
    const answerOptions = document.querySelectorAll('.answer-option');
    if (answerOptions[answerIndex]) {
        answerOptions[answerIndex].click();
    }
}

// Update progress bar
function updateProgressBar() {
    const progressBar = document.querySelector('.quiz-progress-bar');
    const answeredQuestions = document.querySelectorAll('.question-number.answered').length;
    const totalQuestions = getTotalQuestions();
    
    if (progressBar) {
        const percentage = (answeredQuestions / totalQuestions) * 100;
        progressBar.style.width = `${percentage}%`;
        progressBar.setAttribute('aria-valuenow', percentage);
    }
}

// Update question counter
function updateQuestionCounter() {
    const counter = document.querySelector('.question-counter');
    const currentIndex = getCurrentQuestionIndex();
    const totalQuestions = getTotalQuestions();
    
    if (counter) {
        counter.textContent = `Question ${currentIndex + 1} of ${totalQuestions}`;
    }
}

// Mark current question as answered
function markQuestionAnswered() {
    const currentIndex = getCurrentQuestionIndex();
    const questionNumber = document.querySelector(`[data-question-index="${currentIndex}"].question-number`);
    
    if (questionNumber) {
        questionNumber.classList.add('answered');
    }
}

// Save current answer
function saveCurrentAnswer() {
    const currentIndex = getCurrentQuestionIndex();
    const selectedOption = document.querySelector('.answer-option.selected');
    
    if (selectedOption) {
        const answerId = selectedOption.getAttribute('data-answer-id');
        
        // Send AJAX request to save answer
        fetch('/quiz/save-answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                question_index: currentIndex,
                answer_id: answerId
            })
        }).catch(error => {
            console.error('Error saving answer:', error);
        });
    }
}

// Save overall quiz progress
function saveQuizProgress() {
    const answers = collectAllAnswers();
    
    fetch('/quiz/save-progress/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            quiz_session_id: getQuizSessionId(),
            answers: answers,
            current_question: getCurrentQuestionIndex()
        })
    }).catch(error => {
        console.error('Error saving progress:', error);
    });
}

// Submit quiz
function submitQuiz() {
    if (confirm('Are you sure you want to submit your quiz? This action cannot be undone.')) {
        // Mark as submitted
        sessionStorage.setItem('quizSubmitted', 'true');
        
        // Submit form
        const submitForm = document.getElementById('quiz-submit-form');
        if (submitForm) {
            submitForm.submit();
        }
    }
}

// Auto-submit quiz when time runs out
function autoSubmitQuiz() {
    alert('Time\'s up! Your quiz will be submitted automatically.');
    sessionStorage.setItem('quizSubmitted', 'true');
    
    const submitForm = document.getElementById('quiz-submit-form');
    if (submitForm) {
        submitForm.submit();
    }
}

// Utility functions
function getCurrentQuestionIndex() {
    const activeQuestion = document.querySelector('.question-container.active');
    return activeQuestion ? parseInt(activeQuestion.getAttribute('data-question-index')) : 0;
}

function getTotalQuestions() {
    return document.querySelectorAll('.question-number').length;
}

function getQuizSessionId() {
    const sessionElement = document.querySelector('[data-quiz-session-id]');
    return sessionElement ? sessionElement.getAttribute('data-quiz-session-id') : null;
}

function collectAllAnswers() {
    const answers = {};
    const answeredQuestions = document.querySelectorAll('.question-number.answered');
    
    answeredQuestions.forEach(questionNum => {
        const index = questionNum.getAttribute('data-question-index');
        const selectedAnswer = document.querySelector(`[data-question-index="${index}"] .answer-option.selected`);
        
        if (selectedAnswer) {
            answers[index] = selectedAnswer.getAttribute('data-answer-id');
        }
    });
    
    return answers;
}

function getCsrfToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

function updateNavigationButtons() {
    const currentIndex = getCurrentQuestionIndex();
    const totalQuestions = getTotalQuestions();
    
    const prevBtn = document.getElementById('prev-question');
    const nextBtn = document.getElementById('next-question');
    
    if (prevBtn) {
        prevBtn.disabled = currentIndex === 0;
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentIndex === totalQuestions - 1;
    }
}
