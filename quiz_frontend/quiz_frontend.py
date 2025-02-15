# quiz_frontend/quiz_frontend.py
import reflex as rx
from .state import QuizState
from .components import quiz_component

def index():
    return rx.center(
        rx.vstack(
            rx.heading("Welcome to the Quiz App", font_size="2xl"),
            rx.button("Start Quiz", on_click=QuizState.fetch_questions),
            quiz_component(),
            spacing="20px",
        ),
        padding="50px",
    )

app = rx.App(state=QuizState)
app.add_page(index)

if __name__ == "__main__":
    app.serve()
