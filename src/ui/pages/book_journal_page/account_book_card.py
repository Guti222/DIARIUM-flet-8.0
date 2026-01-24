import flet as ft
from typing import Optional
from data.models.lineaAsiento import LineaAsiento

class TAccountBookCard:
    def __init__(self, account_name: str, account_code: str, debe: float, haber: float, listacuentas: list[LineaAsiento]):
        self.account_name = account_name
        self.account_code = account_code
        self.debe = debe
        self.haber = haber
        self.listacuentas = listacuentas

    def _debe_items(self) -> list[ft.Control]:
        items = []
        for cuenta in self.listacuentas:
            if (cuenta.debe or 0) > 0:
                items.append(
                    ft.Row([
                        ft.Text(str(cuenta.id_asiento), color=ft.Colors.GREY_700),
                        ft.Text(f"{float(cuenta.debe or 0):.2f}", color=ft.Colors.GREEN_700),
                    ], spacing=8)
                )
        if not items:
            # Relleno visual cuando no hay partidas en Debe
            items.append(ft.Container(height=24))
        return items

    def _haber_items(self) -> list[ft.Control]:
        items = []
        for cuenta in self.listacuentas:
            if (cuenta.haber or 0) > 0:
                items.append(
                    ft.Row([
                        ft.Text(str(cuenta.id_asiento), color=ft.Colors.GREY_700),
                        ft.Container(
                            content=ft.Text(f"{float(cuenta.haber or 0):.2f}", color=ft.Colors.RED_700),
                            padding=ft.padding.only(left=24)  # sangría para Haber
                        ),
                    ], spacing=8)
                )
        if not items:
            # Relleno visual cuando no hay partidas en Haber
            items.append(ft.Container(height=24))
        return items

    def build(self) -> ft.Control:
        # Paleta y estilos
        azul_fondo = ft.Colors.BLUE_50
        azul_borde = ft.Colors.BLUE_200
        azul_header = ft.Colors.BLUE_100
        azul_texto = ft.Colors.BLUE_800
        grad = ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=[ft.Colors.WHITE, azul_fondo])

        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE, color=azul_texto, size=20),
                ft.Text(f"{self.account_code} - {self.account_name}", weight=ft.FontWeight.BOLD, color=azul_texto),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=8, horizontal=12),
            bgcolor=azul_header,
            border_radius=ft.border_radius.all(8),
        )

        columnas = ft.Row([
            ft.Container(
                expand=True,
                content=ft.Column([
                    ft.Text("Debe", weight=ft.FontWeight.BOLD, color=azul_texto),
                    *self._debe_items(),
                    ft.Container(expand=True),  # empuja contenido para ocupar altura
                ], spacing=6, expand=True),
                border=ft.border.all(1, azul_borde),
                border_radius=ft.border_radius.all(8),
                padding=ft.padding.all(8),
                bgcolor=ft.Colors.WHITE,
            ),
            ft.Container(
                expand=True,
                content=ft.Column([
                    ft.Text("Haber", weight=ft.FontWeight.BOLD, color=azul_texto),
                    *self._haber_items(),
                    ft.Container(expand=True),
                ], spacing=6, expand=True),
                border=ft.border.all(1, azul_borde),
                border_radius=ft.border_radius.all(8),
                padding=ft.padding.all(8),
                bgcolor=ft.Colors.WHITE,
            ),
        ], spacing=16, expand=True, width=400 )

        cuerpo = ft.Container(
            expand=True,
            content=ft.Column([
                header,
                ft.Container(content=columnas, expand=True),
                ft.Container(
                    padding=ft.padding.only(top=8),
                    border=ft.border.only(top=ft.border.BorderSide(1, azul_borde)),
                    content=ft.Container(
                        content=ft.Row([
                            ft.Text("Total", weight=ft.FontWeight.BOLD, color=azul_texto),
                            ft.Row([
                                ft.Text(f"Debe: {self.debe:.2f}", color=ft.Colors.GREEN_700),
                                ft.Container(width=70),
                                ft.Text(" | "),
                                ft.Container(width=80),
                                ft.Text(f"Haber: {self.haber:.2f}", color=ft.Colors.RED_700),
                            ],)
                        ]),
                        expand=True,
                    ),
                    width=400
                ),
            ], expand=True),
            gradient=grad,
            padding=ft.padding.all(16),
            border=ft.border.all(1, azul_borde),
            border_radius=ft.border_radius.all(12),
        )

        return ft.Card(
            content=cuerpo,
            elevation=8,
            shadow_color=ft.Colors.BLUE_200,
        )