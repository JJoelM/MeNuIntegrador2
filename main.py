import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from metodos.gauss_elimination import create_gauss_frame
from metodos.newton_gregory import create_newton_frame
from metodos.integration_methods import create_integration_frame
from metodos.ode_solver import create_ode_frame


class AppNumerica(ttk.Window):
    def __init__(self):
        super().__init__(title="Calculadora MeNu-v1.02", themename="litera")
        self.geometry("800x600")
        self.minsize(600, 500)

        padding = 10
        main_frame = ttk.Frame(self, padding=padding)
        main_frame.pack(fill=BOTH, expand=YES)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=YES)

        gauss_tab = ttk.Frame(self.notebook, padding=padding)
        newton_tab = ttk.Frame(self.notebook, padding=padding)
        integration_tab = ttk.Frame(self.notebook, padding=padding)
        ode_tab = ttk.Frame(self.notebook, padding=padding)

        self.notebook.add(gauss_tab, text="Eliminación de Gauss")
        self.notebook.add(newton_tab, text="Newton-Gregory")
        self.notebook.add(integration_tab, text="Métodos de Integración")
        self.notebook.add(ode_tab, text="Ecuaciones Diferenciales")

        create_gauss_frame(gauss_tab)
        create_newton_frame(newton_tab)
        create_integration_frame(integration_tab)
        create_ode_frame(ode_tab)


if __name__ == "__main__":
    app = AppNumerica()
    app.mainloop()
