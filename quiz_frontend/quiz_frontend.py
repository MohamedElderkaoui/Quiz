import reflex as rx

def index():
    return rx.center(
        rx.vstack(
            rx.heading("Cuestionario Contrarreloj", size="xl"),
            rx.button("Comenzar Juego", on_click=lambda: rx.redirect("/quiz")),
            rx.button("Ver Ranking", on_click=lambda: rx.redirect("/ranking")),
            spacing="4"
        ),
        height="100vh"
    )

app = rx.App()
app.add_page(index, route="/", title="Inicio")
