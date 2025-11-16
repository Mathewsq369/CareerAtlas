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
            const response = await fetch('/assessment/api/questions/');
            this.questions = await response.json();
            
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
            const response = await fetch('/assessment/api/sessions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            const session = await response.json();
            this.sessionId = session.id;
        } catch (error) {
            console.error('Error initializing session:', error);
        }
    }

    showQuestion(index) {
        if (index < 0 || index >= this.questions.length) return;

        this.currentQuestionIndex = index;
        const question = this.questions[index];

        this.questionText.textContent = question.text;
        this.renderAnswerOptions(question);
        this.updateProgress();
        this.updateNavigation();
    }

    renderAnswerOptions(question) {
        this.answerOptions.innerHTML = '';

        question.choices.forEach(choice => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'assessment-option';
            if (this.responses.get(question.id) === choice.id) {
                optionDiv.classList.add('selected');
            }

            optionDiv.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="text-gray-800">${choice.text}</span>
                    <div class="flex items-center space-x-2">
                        <span class="text-sm text-gray-500 px-2 py-1 bg-gray-100 rounded">
                            Value: ${choice.value > 0 ? '+' : ''}${choice.value}
                        </span>
                        <div class="w-4 h-4 border-2 border-gray-300 rounded-full flex items-center justify-center">
                            ${this.responses.get(question.id) === choice.id ? 
                                '<div class="w-2 h-2 bg-blue-600 rounded-full"></div>' : ''}
                        </div>
                    </div>
                </div>
            `;

            optionDiv.addEventListener('click', () => this.selectAnswer(question.id, choice.id));
            this.answerOptions.appendChild(optionDiv);
        });
    }

    async selectAnswer(questionId, choiceId) {
        this.responses.set(questionId, choiceId);
        
        // Save response to server
        await this.saveResponse(questionId, choiceId);
        
        // Update UI
        this.renderAnswerOptions(this.questions[this.currentQuestionIndex]);
        this.updateProgress();
    }

    async saveResponse(questionId, choiceId) {
        if (!this.sessionId || this.isSubmitting) return;

        this.isSubmitting = true;
        
        try {
            await fetch(`/assessment/api/sessions/${this.sessionId}/submit_response/`, {
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
        } catch (error) {
            console.error('Error saving response:', error);
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
        }
    }

    updateProgress() {
        const answeredCount = this.responses.size;
        const totalQuestions = this.questions.length;
        const progress = (answeredCount / totalQuestions) * 100;

        this.progressBar.style.width = `${progress}%`;
        this.progressText.textContent = `${Math.round(progress)}%`;

        // Update question counter
        const questionCounter = document.getElementById('question-counter');
        if (questionCounter) {
            questionCounter.textContent = `Question ${this.currentQuestionIndex + 1} of ${totalQuestions}`;
        }
    }

    updateNavigation() {
        this.prevBtn.disabled = this.currentQuestionIndex === 0;
        
        const isLastQuestion = this.currentQuestionIndex === this.questions.length - 1;
        this.nextBtn.style.display = isLastQuestion ? 'none' : 'block';
        this.finishBtn.style.display = isLastQuestion ? 'block' : 'none';
        
        // Enable finish button only if all questions are answered
        this.finishBtn.disabled = this.responses.size < this.questions.length;
    }

    async finishAssessment() {
        if (this.responses.size < this.questions.length) {
            if (!confirm('You haven\'t answered all questions. Are you sure you want to finish?')) {
                return;
            }
        }

        this.showLoading('Generating your results...');

        try {
            const response = await fetch(`/assessment/api/sessions/${this.sessionId}/complete_assessment/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (response.ok) {
                window.location.href = '/assessment/results/';
            } else {
                throw new Error('Failed to complete assessment');
            }
        } catch (error) {
            console.error('Error completing assessment:', error);
            this.showError('Failed to complete assessment. Please try again.');
        }
    }

    hideLoading() {
        this.loadingSpinner.style.display = 'none';
        this.questionContainer.style.display = 'block';
    }

    showLoading(message = 'Loading...') {
        this.loadingSpinner.innerHTML = `
            <div class="text-center">
                <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p class="mt-4 text-gray-600">${message}</p>
            </div>
        `;
        this.loadingSpinner.style.display = 'block';
        this.questionContainer.style.display = 'none';
    }

    showError(message) {
        this.loadingSpinner.innerHTML = `
            <div class="text-center text-red-600">
                <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                <p class="text-lg font-semibold">${message}</p>
                <button onclick="location.reload()" class="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded">
                    Retry
                </button>
            </div>
        `;
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Initialize assessment when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('question-container')) {
        window.assessmentEngine = new AssessmentEngine();
    }
});