from typing import List, Dict, Any
import reflex as rx
import requests

class QuizState(rx.State):
    # A list of questions, where each question is a dict.
    questions: List[Dict[str, Any]] = []
    current_question_index: int = 0
    selected_answers: List[Any] = []
    score: int = 0
    quiz_completed: bool = False

    @rx.var(cache=True)
    def current_question_text(self) -> str:
        if self.questions:
            return self.questions[self.current_question_index].get("text", "No question available")
        return "No question available"

    @rx.var(cache=True)
    def current_question_answers(self) -> List[Dict[str, Any]]:
        if self.questions:
            # Expecting a list of answer dictionaries.
            return self.questions[self.current_question_index].get("answers", [])
        return []

    @rx.var(cache=True)
    def current_question_id(self) -> int:
        if self.questions:
            return self.questions[self.current_question_index].get("id", 0)
        return 0

    @rx.var(cache=True)
    def quiz_result(self) -> str:
        return f"Quiz Completed! Your score: {self.score}"

    def fetch_questions(self):
        response = requests.get("http://localhost:8000/api/questions/random/")
        if response.status_code == 200:
            self.questions = response.json()
            self.current_question_index = 0
            self.quiz_completed = False
            self.score = 0
            self.selected_answers = []
        else:
            rx.window_alert("Error fetching questions.")

    def select_answer(self, question_id, answer_id):
        self.selected_answers.append((question_id, answer_id))
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
        else:
            self.calculate_score()
            self.quiz_completed = True

    def calculate_score(self):
        # Dummy logic: count every selected answer as correct.
        correct_answers = 0
        for question_id, answer_id in self.selected_answers:
            correct_answers += 1
        self.score = correct_answers
