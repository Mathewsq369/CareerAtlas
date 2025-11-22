// Assessment JavaScript for dynamic question handling
class AssessmentEngine {
    constructor() {
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.responses = new Map();
        this.sessionId = null;
        this.isSubmitting = false;
        
        this.initializeElements();
        this.loadQuestions();
    }

    initializeElements() {
        this.questionContainer = document.getElementById('question-container');
        this.loadingSpinner = document.getElementById('loading-spinner');
        this.questionText = document.getElementById('question-text');
        this.answerOptions = document.getElementById('answer-options');
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.finishBtn = document.getElementById('finish-btn');
        this.progressBar = document.getElementById('progress-bar');
        this.progressText = document.getElementById('progress-text');

        this.bindEvents();
    }

    bindEvents() {
        this.prevBtn.addEventListener('click', () => this.previousQuestion());
        this.nextBtn.addEventListener('click', () => this.nextQuestion());
        this.finishBtn.addEventListener('click', () => this.finishAssessment());
    }

    async loadQuestions() {
        try {
            console.log('Loading questions from API...');
            
            // FIXED: Correct URL path (plural 'assessments')
            const response = await fetch('/assessments/api/questions/');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.questions = await response.json();
            console.log(`Loaded ${this.questions.length} questions:`, this.questions);
            
            // Initialize session
            await this.initializeSession();
            
            this.hideLoading();
            this.showQuestion(0);
        } catch (error) {
            console.error('Error loading questions:', error);
            this.showError('Failed to load questions. Please refresh the page.');
        }
    }

    async initializeSession() {
        try {
            console.log('Initializing assessment session...');
            
            // FIXED: Correct URL path
            const response = await fetch('/assessments/api/sessions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({})
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const session = await response.json();
            this.sessionId = session.id;
            console.log('Session initialized with ID:', this.sessionId);
            
        } catch (error) {
            console.error('Error initializing session:', error);
            // Continue without session for demo purposes
            this.sessionId = 'demo-session';
        }
    }

    showQuestion(index) {
        if (index < 0 || index >= this.questions.length) {
            console.error('Invalid question index:', index);
            return;
        }

        this.currentQuestionIndex = index;
        const question = this.questions[index];

        console.log('Showing question:', question);

        this.questionText.textContent = question.text;
        this.renderAnswerOptions(question);
        this.updateProgress();
        this.updateNavigation();
    }

    renderAnswerOptions(question) {
        this.answerOptions.innerHTML = '';

        if (!question.choices || question.choices.length === 0) {
            this.answerOptions.innerHTML = '<p class="text-red-500">No answer options available</p>';
            return;
        }

        question.choices.forEach(choice => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'answer-option w-full text-left p-4 border-2 border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition duration-200 cursor-pointer';
            
            if (this.responses.get(question.id) === choice.id) {
                optionDiv.classList.add('bg-blue-50', 'border-blue-300');
            }

            optionDiv.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="flex-1 text-gray-800 text-left">${choice.text}</span>
                    <div class="flex items-center space-x-2">
                        <span class="text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">
                            Value: ${choice.value > 0 ? '+' : ''}${choice.value}
                        </span>
                        <i class="fas fa-chevron-right text-blue-500 ml-2"></i>
                    </div>
                </div>
            `;

            optionDiv.addEventListener('click', () => this.selectAnswer(question.id, choice.id));
            this.answerOptions.appendChild(optionDiv);
        });
    }

    async selectAnswer(questionId, choiceId) {
        console.log(`Selected answer for question ${questionId}: ${choiceId}`);
        
        this.responses.set(questionId, choiceId);
        
        // Save response to server
        await this.saveResponse(questionId, choiceId);
        
        // Update UI
        this.renderAnswerOptions(this.questions[this.currentQuestionIndex]);
        this.updateProgress();
        this.updateNavigation();
    }

    async saveResponse(questionId, choiceId) {
        if (!this.sessionId || this.isSubmitting) return;

        this.isSubmitting = true;
        
        try {
            // FIXED: Correct URL path
            const response = await fetch(`/assessments/api/sessions/${this.sessionId}/submit_response/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    question_id: questionId,
                    answer_id: choiceId,
                    response_time: Math.floor(Math.random() * 10) + 1 // Simulate response time
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            console.log('Response saved successfully');
            
        } catch (error) {
            console.error('Error saving response:', error);
            // Don't show error to user for failed saves, just log it
        } finally {
            this.isSubmitting = false;
        }
    }

    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.showQuestion(this.currentQuestionIndex - 1);
        }
    }

    nextQuestion() {
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.showQuestion(this.currentQuestionIndex + 1);
        } else {
            // If we're on the last question and user clicks next, show completion
            this.showCompletionOptions();
        }
    }

    showCompletionOptions() {
        const answeredCount = this.responses.size;
        const totalQuestions = this.questions.length;
        
        this.questionContainer.innerHTML = `
            <div class="bg-white rounded-lg shadow-md p-8 text-center">
                <div class="mb-6">
                    <i class="fas fa-check-circle text-green-500 text-6xl mb-4"></i>
                    <h2 class="text-2xl font-bold text-gray-800 mb-2">Assessment Complete!</h2>
                    <p class="text-gray-600 mb-4">
                        You've answered ${answeredCount} out of ${totalQuestions} questions.
                    </p>
                    ${answeredCount < totalQuestions ? 
                        '<p class="text-yellow-600 text-sm mb-4">You can still go back and answer remaining questions.</p>' : 
                        '<p class="text-green-600 text-sm mb-4">All questions answered! Ready to see your results.</p>'
                    }
                </div>
                
                <div class="space-y-4 max-w-md mx-auto">
                    <button onclick="assessmentEngine.finishAssessment()" 
                            class="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-lg font-semibold transition duration-200">
                        <i class="fas fa-chart-bar mr-2"></i>View My Results
                    </button>
                    
                    <button onclick="assessmentEngine.showQuestion(0)" 
                            class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold transition duration-200">
                        <i class="fas fa-redo mr-2"></i>Review Answers
                    </button>
                </div>
            </div>
        `;
    }

    updateProgress() {
        const answeredCount = this.responses.size;
        const totalQuestions = this.questions.length;
        const progress = totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0;

        if (this.progressBar) {
            this.progressBar.style.width = `${progress}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = `${Math.round(progress)}%`;
        }

        // Update question counter
        const questionCounter = document.getElementById('question-counter');
        if (questionCounter && totalQuestions > 0) {
            questionCounter.textContent = `Question ${this.currentQuestionIndex + 1} of ${totalQuestions}`;
        }
    }

    updateNavigation() {
        if (!this.prevBtn || !this.nextBtn || !this.finishBtn) return;

        this.prevBtn.disabled = this.currentQuestionIndex === 0;
        
        const isLastQuestion = this.currentQuestionIndex === this.questions.length - 1;
        
        if (this.nextBtn) {
            this.nextBtn.style.display = isLastQuestion ? 'none' : 'block';
        }
        if (this.finishBtn) {
            this.finishBtn.style.display = isLastQuestion ? 'block' : 'none';
            this.finishBtn.disabled = this.responses.size < this.questions.length;
        }
    }

    async finishAssessment() {
        const answeredCount = this.responses.size;
        const totalQuestions = this.questions.length;

        if (answeredCount < totalQuestions) {
            const proceed = confirm(`You have answered ${answeredCount} out of ${totalQuestions} questions. Are you sure you want to finish the assessment?`);
            if (!proceed) {
                return;
            }
        }

        this.showLoading('Generating your results...');

        try {
            // FIXED: Correct URL path
            const response = await fetch(`/assessments/api/sessions/${this.sessionId}/complete_assessment/`, {
                method: 'POST',
                headers: {
                    'X-CSRRF-Token': this.getCsrfToken()
                }
            });

            if (response.ok) {
                console.log('Assessment completed successfully, redirecting...');
                window.location.href = '/assessments/results/';
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        } catch (error) {
            console.error('Error completing assessment:', error);
            this.showError('Failed to complete assessment. Please try again.');
        }
    }

    hideLoading() {
        if (this.loadingSpinner) {
            this.loadingSpinner.style.display = 'none';
        }
        if (this.questionContainer) {
            this.questionContainer.style.display = 'block';
        }
    }

    showLoading(message = 'Loading...') {
        if (this.loadingSpinner) {
            this.loadingSpinner.innerHTML = `
                <div class="text-center py-8">
                    <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                    <p class="text-gray-600 text-lg">${message}</p>
                </div>
            `;
            this.loadingSpinner.style.display = 'block';
        }
        if (this.questionContainer) {
            this.questionContainer.style.display = 'none';
        }
    }

    showError(message) {
        if (this.loadingSpinner) {
            this.loadingSpinner.innerHTML = `
                <div class="text-center text-red-600 py-8">
                    <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                    <p class="text-lg font-semibold mb-4">${message}</p>
                    <button onclick="location.reload()" class="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg transition duration-200">
                        <i class="fas fa-refresh mr-2"></i>Retry
                    </button>
                </div>
            `;
            this.loadingSpinner.style.display = 'block';
        }
        if (this.questionContainer) {
            this.questionContainer.style.display = 'none';
        }
    }

    getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
}

// Initialize assessment when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing assessment engine...');
    
    if (document.getElementById('question-container')) {
        window.assessmentEngine = new AssessmentEngine();
        console.log('Assessment engine initialized');
    } else {
        console.log('No assessment container found');
    }
});