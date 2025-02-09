from django.contrib import admin
from django.http import HttpResponse
import csv
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from .models import Question, Answer, Score

# 🔹 Función para exportar puntuaciones a CSV
def export_scores_to_csv(modeladmin, request, queryset=None):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scores.csv"'
    writer = csv.writer(response, csv.excel, delimiter=',')

    # Escribir encabezados
    writer.writerow(['Jugador', 'Puntos', 'Fecha'])

    # Obtener los datos a exportar (todos o filtrados)
    scores = queryset if queryset else Score.objects.all()
    for score in scores:
        writer.writerow([score.player_name, score.points, score.date.strftime('%Y-%m-%d %H:%M:%S')])

    return response

export_scores_to_csv.short_description = "📥 Exportar puntuaciones a CSV"

# 🔹 Inline para mostrar respuestas dentro de la pregunta
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ['text', 'is_correct']

# 🔹 Configuración del modelo Question en el admin
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz_category', 'difficulty')
    list_filter = ('quiz_category', 'difficulty')
    search_fields = ('text',)
    ordering = ('difficulty',)
    inlines = [AnswerInline]

# 🔹 Configuración del modelo Score en el admin (con botón de exportación)
@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'points', 'date')
    list_filter = ('date',)
    search_fields = ('player_name',)
    ordering = ('-points',)
    actions = [export_scores_to_csv]
    actions_on_top = True
    change_list_template = "admin/score_change_list.html"  # Plantilla personalizada

    # Agregar URL para exportar CSV desde un botón
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-csv/', self.admin_site.admin_view(self.export_all_scores), name='score_export_csv'),
        ]
        return custom_urls + urls

    # Vista para exportar todas las puntuaciones
    def export_all_scores(self, request):
        return export_scores_to_csv(self, request)

# 🔹 Configuración del modelo Answer en el admin
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)
