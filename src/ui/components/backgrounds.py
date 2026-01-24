import flet as ft

def create_modern_background(page: ft.Page):
    """
    Componente de fondo decorativo moderno
    """
    primary_blue = "#0D47A1" 
    
    fondo_decorativo = ft.Stack(
        [
            ft.Container(
                width=page.window_width * 2,
                height=page.window_height * 2,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    [
                        ft.Container(
                            width=page.window_width * 2,
                            height=200,
                            bgcolor=primary_blue,
                            content=ft.Column(
                                [
                                    ft.Container(
                                        width=page.window_width * 2,
                                        height=40,
                                    ),
                                    ft.Container(
                                        width=page.window_width * 2,
                                        height=160,
                                        bgcolor=ft.Colors.WHITE,
                                        border_radius=ft.border_radius.only(
                                            top_right=300,
                                        ),
                                    )
                                ]
                            )
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            width=page.window_width * 2,
                            height=200,
                            bgcolor=primary_blue,
                            content=ft.Column(
                                [
                                    ft.Container(
                                        width=page.window_width * 2,
                                        height=160,
                                        bgcolor=ft.Colors.WHITE,
                                        border_radius=ft.border_radius.only(
                                            bottom_left=300,
                                        ),
                                    ),
                                    ft.Container(
                                        width=page.window_width * 2,
                                        height=40,
                                    ),
                                ]
                            )
                        ),
                    ]
                )
            )
        ]
    )
    
    return ft.Stack([fondo_decorativo], expand=True)