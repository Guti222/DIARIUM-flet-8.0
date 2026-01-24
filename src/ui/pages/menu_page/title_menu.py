import flet as ft

def titlemenu():
    
    return ft.Container(
        
        content=ft.Row(
            [
                ft.Image(
                src="assets/images/contabilidad.png",
                width=150,
                height=150,
            ),
            ft.Text(
                "Diarium \nAplicación de creación\nde libros contables ",
                size=30,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
                text_align=ft.TextAlign.LEFT,
            ),
            ]
        )
    )