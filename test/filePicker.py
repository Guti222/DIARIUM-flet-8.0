import flet as ft

async def main(page: ft.Page):
    # En la 1.0/0.80.5 el FilePicker se configura así:
    fp = ft.FilePicker()
    fp.on_result = lambda e: print(f"Seleccionado: {e.files}")
    
    page.overlay.append(fp)
    
    # En esta versión, update() dentro de async main suele no requerir await
    # Pero si te da error de 'NoneType', simplemente quita el 'await'
    page.update()

    async def pick_files_handler(e):
        await fp.pick_files_async()

    page.add(
        ft.Text("DIARIUM - v0.80.5 Limpio"),
        ft.Button("Abrir Selector", on_click=pick_files_handler)
    )

if __name__ == "__main__":
    ft.run(main)