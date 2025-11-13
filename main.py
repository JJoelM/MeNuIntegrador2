import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Importamos las funciones que crean la UI de cada método
# Cada archivo .py es responsable de crear su propio frame (panel)
from metodos.gauss_elimination import create_gauss_frame
from metodos.newton_gregory import create_newton_frame


class AppNumerica(ttk.Window):
    def __init__(self):
        # Usamos el tema 'litera' que es limpio y profesional
        super().__init__(title="Calculadora de Métodos Numéricos", themename="litera")
        self.geometry("800x600")
        self.minsize(600, 500)

        # Contenedor principal
        padding = 10
        main_frame = ttk.Frame(self, padding=padding)
        main_frame.pack(fill=BOTH, expand=YES)

        # Selector de Métodos (Punto 1)
        # Usamos un Notebook (pestañas) para una UI limpia
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=YES)

        # Creamos los frames para cada pestaña
        gauss_tab = ttk.Frame(self.notebook, padding=padding)
        newton_tab = ttk.Frame(self.notebook, padding=padding)

        # Añadimos las pestañas al notebook
        self.notebook.add(gauss_tab, text="Eliminación de Gauss")
        self.notebook.add(newton_tab, text="Newton-Gregory")

        # --- Invocamos a cada módulo para que "dibuje" su UI ---
        # Pasamos el 'frame' padre (la pestaña) a la función
        create_gauss_frame(gauss_tab)
        create_newton_frame(newton_tab)


if __name__ == "__main__":
    app = AppNumerica()
    app.mainloop()
