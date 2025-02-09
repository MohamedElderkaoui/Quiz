import reflex as rx
import json
import asyncio
import websockets

# Estado del cuestionario
class QuizState(rx.State):
    question: str = "Cargando pregunta..."
    answers: list = []
    correct_answer: str = ""
    seconds_remaining: int = 30
    score: int = 0
    question_index: int = 0
    game_over: bool = False

    async def fetch_question(self):
        """Obtiene una pregunta del backend Django."""
        resp = await rx.get("/api/questions/")
        data = resp.json()
        if data:
            question_data = data[self.question_index]
            self.question = question_data["text"]
            self.answers = [answer["text"] for answer in question_data["answers"]]
            self.correct_answer = next(a["text"] for a in question_data["answers"] if a["is_correct"])
            self.seconds_remaining = 30

    async def start_timer(self):
        """Conecta con WebSocket y maneja el tiempo."""
        async with websockets.connect("ws://127.0.0.1:8000/ws/quiz/timer/") as ws:
            while self.seconds_remaining > 0:
                msg = await ws.recv()
                data = json.loads(msg)
                self.seconds_remaining = data["seconds_remaining"]
                await asyncio.sleep(1)
                if self.seconds_remaining == 0:
                    self.next_question()

    def check_answer(self, answer):
        """Verifica la respuesta y actualiza el puntaje."""
        if answer == self.correct_answer:
            self.score += self.seconds_remaining  # Puntos = tiempo restante
        self.next_question()

    def next_question(self):
        """Carga la siguiente pregunta o finaliza el juego."""
        if self.question_index < 9:
            self.question_index += 1
            self.fetch_question()
        else:
            self.game_over = True
            rx.redirect("/results")

def quiz():
    return rx.center(
        rx.vstack(
            rx.heading("Pregunta:", size="lg"),
            rx.text(QuizState.question),
            rx.foreach(QuizState.answers, lambda answer: rx.button(answer, on_click=lambda: QuizState.check_answer(answer))),
            rx.text(f"Tiempo restante: {QuizState.seconds_remaining} s"),
            spacing="4"
        ),
        height="100vh"
    )

app.add_page(quiz, route="/quiz", title="Juego")
