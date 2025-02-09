import reflex as rx

class RankingState(rx.State):
    ranking: list = []

    async def get_ranking(self):
        """Obtiene los mejores puntajes del backend Django."""
        resp = await rx.get("/api/ranking/")
        self.ranking = resp.json()

def ranking():
    return rx.center(
        rx.vstack(
            rx.heading("Ranking de Jugadores", size="xl"),
            rx.foreach(RankingState.ranking, lambda score: rx.text(f"{score['player_name']}: {score['points']} pts")),
            rx.button("Volver al Inicio", on_click=lambda: rx.redirect("/")),
            spacing="4"
        ),
        height="100vh"
    )

app.add_page(ranking, route="/ranking", title="Ranking")
