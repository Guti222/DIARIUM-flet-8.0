import flet as ft
from typing import List, Callable, Optional


def create_autocomplete_field(
    suggestions: List[dict],  # [{"code": "1", "name": "Activo", "type": "Activo"}, ...]
    on_select: Optional[Callable] = None,
    width: int = 160,
    hint_text: str = "Buscar...",
):
    """Crear un campo de autocomplete estilo Google"""
    
    filtered_suggestions = []
    selected_item = {"value": None}
    
    # Componentes
    text_field = ft.TextField(
        hint_text=hint_text,
        width=width,
        autofocus=False,
    )
    
    suggestions_list = ft.ListView(
        controls=[],
        spacing=0,
        height=0,
        visible=False,
    )
    
    backdrop = ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        on_click=lambda e: hide_suggestions(),
    )
    
    # Funciones internas
    def on_suggestion_click(suggestion: dict):
        """Cuando el usuario selecciona una sugerencia"""
        selected_item["value"] = suggestion
        text_field.value = suggestion.get("code", "")
        hide_suggestions()
        
        # Ejecutar callback si existe
        if on_select:
            on_select(suggestion)
    
    def create_suggestion_item(suggestion: dict) -> ft.Container:
        """Crear un item de sugerencia clickeable"""
        item_container = ft.Container(
            content=ft.ListTile(
                leading=ft.Text(
                    suggestion.get("code", ""),
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_700,
                ),
                title=ft.Text(suggestion.get("name", ""), size=13),
                trailing=ft.Text(
                    suggestion.get("type", ""),
                    size=11,
                    color=ft.Colors.BLUE_700,
                ),
                dense=True,
                on_click=lambda e, item=suggestion: on_suggestion_click(item),
            ),
            on_hover=lambda e: on_item_hover(e, item_container),
        )
        return item_container
    
    def on_item_hover(e, container):
        """Cambiar color al pasar el mouse"""
        if e.data == "true":
            container.bgcolor = ft.Colors.BLUE_50
        else:
            container.bgcolor = None
        container.update()
    
    def show_suggestions():
        """Mostrar la lista de sugerencias"""
        items = [create_suggestion_item(s) for s in filtered_suggestions[:10]]
        
        suggestions_list.controls = items
        suggestions_list.height = min(len(items) * 56, 280)
        suggestions_list.visible = True
        backdrop.visible = True
        suggestions_container.visible = True
        suggestions_container.height = min(len(items) * 56, 280)
        container.update()
    
    def hide_suggestions():
        """Ocultar la lista de sugerencias"""
        suggestions_list.visible = False
        suggestions_list.height = 0
        backdrop.visible = False
        suggestions_container.visible = False
        suggestions_container.height = 0
        container.update()
    
    def on_text_change(e):
        """Filtrar sugerencias cuando el usuario escribe"""
        query = text_field.value.strip().lower()
        
        if not query:
            hide_suggestions()
            return
        
        # Filtrar sugerencias
        nonlocal filtered_suggestions
        filtered_suggestions = [
            s for s in suggestions
            if query in s.get("code", "").lower() or
               query in s.get("name", "").lower()
        ]
        
        if filtered_suggestions:
            show_suggestions()
        else:
            hide_suggestions()
    
    def on_focus(e):
        """Mostrar sugerencias cuando el campo obtiene foco"""
        if text_field.value.strip():
            on_text_change(None)
    
    def on_blur(e):
        """Cerrar sugerencias cuando el campo pierde foco"""
        # Pequeño delay para permitir el click en las sugerencias
        import asyncio
        try:
            asyncio.get_event_loop().call_later(0.2, hide_suggestions)
        except:
            hide_suggestions()
    
    # Asignar eventos
    text_field.on_change = on_text_change
    text_field.on_focus = on_focus
    text_field.on_blur = on_blur
    
    # Construir el contenedor
    suggestions_container = ft.Container(
        content=ft.Stack(
            [
                backdrop,
                suggestions_list,
            ],
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
        ),
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        visible=False,
        height=0,
    )
    
    container = ft.Column(
        [
            text_field,
            suggestions_container,
        ],
        spacing=0,
    )
    
    # Retornar objeto con métodos útiles
    class AutocompleteResult:
        def get_value(self) -> str:
            return text_field.value.strip()
        
        def get_selected(self) -> Optional[dict]:
            return selected_item["value"]
        
        def set_value(self, value: str):
            text_field.value = value
            container.update()
        
        def get_control(self):
            return container
    
    return AutocompleteResult()
