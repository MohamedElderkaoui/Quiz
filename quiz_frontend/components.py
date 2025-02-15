import reflex as rx
from .state import QuizState

def render_answer(answer):
    # Unwrap the reactive variable: use .value if available.
    ans = answer.value if hasattr(answer, "value") else answer
    return rx.button(
        ans["text"],
        on_click=lambda: QuizState.select_answer(
            QuizState.current_question_id,
            ans["id"]
        ),
        width="100%",
        padding="10px",
        margin="5px 0",
    )

def question_component():
    return rx.box(
        rx.text(QuizState.current_question_text, font_size="xl", font_weight="bold"),
        rx.vstack(
            rx.foreach(
                # Pass the computed list directly.
                QuizState.current_question_answers,
                render_answer
            ),
            align_items="start",
        ),
        padding="20px",
        border="1px solid #ccc",
        border_radius="8px",
        box_shadow="md",
        margin="20px 0",
    )

def quiz_component():
    return rx.cond(
        QuizState.quiz_completed,
        rx.box(
            rx.text(QuizState.quiz_result, font_size="2xl"),
            rx.button("Restart Quiz", on_click=QuizState.fetch_questions),
            text_align="center",
            padding="20px",
        ),
        question_component(),
    )
