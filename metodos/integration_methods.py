import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np

# Lista para mantener referencia a los widgets Entry de los puntos
points_entries = []


def create_integration_frame(parent_frame):
    """Crea la UI para los Métodos de Integración Numérica."""

    n_var = ttk.IntVar(value=4)
    method_var = ttk.StringVar(value="automatic")  # 'automatic', 'trapezoid', 'simpson13', 'simpson38'

    # --- Frames de UI ---
    # Controles
    input_frame = ttk.Frame(parent_frame)
    input_frame.pack(fill=X, pady=5)

    # Tabla de puntos
    points_frame = ttk.Frame(parent_frame)
    points_frame.pack(fill=X, pady=10)

    # Selector de método y botón de cálculo
    controls_frame = ttk.Labelframe(parent_frame, text="Selector de Método", padding=10)
    controls_frame.pack(fill=X, pady=5)

    calc_frame = ttk.Frame(parent_frame, padding=10)
    calc_frame.pack(fill=X)

    # Resultados
    results_frame = ttk.Labelframe(parent_frame, text="Resultados (Paso a Paso)", padding=10)
    results_frame.pack(fill=BOTH, expand=YES, pady=5)

    # --- Controles de Entrada ---
    ttk.Label(input_frame, text="Número de Puntos (n):").pack(side=LEFT, padx=5)
    n_spinbox = ttk.Spinbox(input_frame, from_=2, to=20, textvariable=n_var, width=5)
    n_spinbox.pack(side=LEFT, padx=5)

    create_btn = ttk.Button(
        input_frame,
        text="Generar Tabla",
        command=lambda: generate_points_grid(n_var.get(), points_frame),
        bootstyle=SECONDARY
    )
    create_btn.pack(side=RIGHT, padx=10)

    # --- Selector de Método ---
    auto_radio = ttk.Radiobutton(controls_frame, text="Automático (Recomendado)", variable=method_var,
                                 value="automatic")
    auto_radio.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    trap_radio = ttk.Radiobutton(controls_frame, text="Trapecio (Compuesto)", variable=method_var, value="trapezoid")
    trap_radio.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    s13_radio = ttk.Radiobutton(controls_frame, text="Simpson 1/3 (Compuesto)", variable=method_var, value="simpson13")
    s13_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    s38_radio = ttk.Radiobutton(controls_frame, text="Simpson 3/8 (Compuesto)", variable=method_var, value="simpson38")
    s38_radio.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    controls_frame.columnconfigure(0, weight=1)
    controls_frame.columnconfigure(1, weight=1)

    # --- Frame Calculo ---
    solve_btn = ttk.Button(
        calc_frame,
        text="Calcular Integración",
        command=lambda: solve_integration(
            n_var, method_var, results_text
        ),
        bootstyle=SUCCESS
    )
    solve_btn.pack(fill=X, expand=YES)

    # --- Área de Resultados ---
    results_text = ScrolledText(results_frame, width=70, height=15, state="disabled", wrap="word")
    results_text.pack(fill=BOTH, expand=YES)

    # Etiquetas de estilo para la salida
    results_text.tag_config("title", font=("Helvetica", 14, "bold"), foreground="blue")
    results_text.tag_config("step", font=("Courier", 12, "italic"), foreground="gray")
    results_text.tag_config("calc", font=("Courier", 12))
    results_text.tag_config("solution", font=("Helvetica", 12, "bold"), foreground="green")
    results_text.tag_config("error", font=("Helvetica", 12, "bold"), foreground="red")
    results_text.tag_config("warn", font=("Helvetica", 12, "bold"), foreground="orange")

    # Generar la tabla de puntos inicial (ej. 4 puntos)
    generate_points_grid(n_var.get(), points_frame)


def generate_points_grid(n, frame):
    """Genera dinámicamente la cuadrícula para los puntos (xi, yi)."""
    global points_entries

    # Limpiar el frame anterior
    for widget in frame.winfo_children():
        widget.destroy()
    points_entries.clear()

    # --- Cabeceras (xi, yi) ---
    ttk.Label(frame, text="Punto (i)", bootstyle="secondary").grid(row=0, column=0, padx=5, pady=2)
    ttk.Label(frame, text="Valor X (x_i)", bootstyle="secondary").grid(row=0, column=1, padx=5, pady=2)
    ttk.Label(frame, text="Valor Y (f(x_i))", bootstyle="secondary").grid(row=0, column=2, padx=5, pady=2)

    # --- Matriz de Entradas ---
    for i in range(n):
        row_label = ttk.Label(frame, text=f"P{i}")
        row_label.grid(row=i + 1, column=0, padx=5, sticky="e")

        entry_x = ttk.Entry(frame, width=15, justify="center")
        entry_x.grid(row=i + 1, column=1, padx=5, pady=5)

        entry_y = ttk.Entry(frame, width=15, justify="center")
        entry_y.grid(row=i + 1, column=2, padx=5, pady=5)

        points_entries.append((entry_x, entry_y))

    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=2)
    frame.grid_columnconfigure(2, weight=2)


def solve_integration(n_var, method_var, results_text):
    """Punto de entrada: Valida y despacha al método de integración correcto."""
    global points_entries

    # --- Preparar UI de Resultados ---
    results_text.config(state="normal")
    results_text.delete("1.0", END)

    def log(message, tag=None):
        if tag:
            results_text.insert(END, message + "\n", tag)
        else:
            results_text.insert(END, message + "\n")
        results_text.see(END)
        results_text.update_idletasks()

    # --- Validación de Entradas ---
    try:
        n = n_var.get()
        method = method_var.get()

        x = []
        y = []

        if len(points_entries) != n:
            log("Error: El número de puntos no coincide. Presiona 'Generar Tabla' de nuevo.", "error")
            return

        for i, (entry_x, entry_y) in enumerate(points_entries):
            val_x = entry_x.get()
            val_y = entry_y.get()
            if not val_x or not val_y:
                raise ValueError(f"El punto P{i} está vacío.")
            x.append(float(val_x))
            y.append(float(val_y))

        # --- Validaciones ---
        # Equidistancia
        if n < 2:
            log("Error: Se necesitan al menos 2 puntos.", "error")
            return

        h = np.round(x[1] - x[0], 9)  # Calcular h inicial
        if h <= 0:
            raise ValueError("Los valores de X deben ser crecientes.")

        for i in range(1, n - 1):
            h_i = np.round(x[i + 1] - x[i], 9)
            if not np.isclose(h, h_i):
                log(f"Error: Los valores de X NO son equidistantes.", "error")
                log(f"  h entre P0 y P1 = {h}", "error")
                log(f"  h entre P{i} y P{i + 1} = {h_i}", "error")
                return

        N = n - 1  # Número de segmentos
        log(f"Validación exitosa: {n} puntos ({N} segmentos) equidistantes con h = {h}\n", "step")

    except ValueError as e:
        log(f"Error de Entrada: {e}", "error")
        return
    finally:
        results_text.config(state="disabled")  # Bloquear temporalmente

    # --- Enviar al Método de Cálculo ---
    results_text.config(state="normal")  # Desbloquear para los logs

    try:
        if method == "automatic":
            solve_automatic(x, y, h, N, log)

        elif method == "trapezoid":
            # --- Validación ---
            # Trapecio siempre es válido si N >= 1 (esto ya está validado)
            log("Iniciando Regla del Trapecio (Compuesto)", "title")
            solve_trapecio(x, y, h, N, log)

        elif method == "simpson13":
            # --- Validación ---
            # N debe ser par y N >= 2
            if N % 2 != 0 or N < 2:
                log("Error de Validación (Simpson 1/3)", "error")
                log("Este método requiere un número PAR de segmentos (ej. 2, 4, 6...).", "error")
                log(f"  -> Esto significa un número IMPAR de puntos (ej. 3, 5, 7...).", "error")
                log(f"  Usted proporcionó {N} segmentos ({n} puntos).", "error")
                return
            log("Iniciando Regla de Simpson 1/3 (Compuesto)", "title")
            solve_simpson13(x, y, h, N, log)

        elif method == "simpson38":
            # --- Validación ---
            # N debe ser MÚLTIPLO DE 3 y N >= 3
            if N % 3 != 0 or N < 3:
                log("Error de Validación (Simpson 3/8)", "error")
                log("Este método requiere un número de segmentos MÚLTIPLO DE 3 (ej. 3, 6, 9...).", "error")
                log(f"  -> Esto significa 4, 7, 10... puntos.", "error")
                log(f"  Usted proporcionó {N} segmentos ({n} puntos).", "error")
                return
            log("Iniciando Regla de Simpson 3/8 (Compuesto)", "title")
            solve_simpson38(x, y, h, N, log)

    except Exception as e:
        log(f"\nError inesperado durante el cálculo: {e}", "error")
    finally:
        results_text.config(state="disabled")


# --- Métodos Individuales ---

def solve_trapecio(x, y, h, N, log, silent=False):
    """Calcula la integral usando la Regla del Trapecio (Compuesto)."""
    if not silent:
        log("Fórmula: (h/2) * [y₀ + 2*Σ(yᵢ) + yₙ]", "calc")

    if N == 1:  # Caso simple
        I = (h / 2) * (y[0] + y[1])
        if not silent:
            log(f"  I = ({h}/2) * ({y[0]} + {y[1]})", "calc")
    else:  # Caso compuesto
        sum_mid = np.sum(y[1:-1])
        I = (h / 2) * (y[0] + 2 * sum_mid + y[-1])
        if not silent:
            log(f"  I = ({h}/2) * ({y[0]} + 2 * ({sum_mid:.4f}) + {y[-1]})", "calc")

    if not silent:
        log(f"\nResultado (Trapecio):", "title")
        log(f"  Integral ≈ {I:.8f}", "solution")
    return I


def solve_simpson13(x, y, h, N, log, silent=False):
    """Calcula la integral usando Simpson 1/3 (Compuesto). Asume N es par."""
    if not silent:
        log("Fórmula: (h/3) * [y₀ + 4*Σ(y_impar) + 2*Σ(y_par) + yₙ]", "calc")

    sum_odd = np.sum(y[1:-1:2])  # Índices 1, 3, 5...
    sum_even = np.sum(y[2:-1:2])  # Índices 2, 4, 6...

    I = (h / 3) * (y[0] + 4 * sum_odd + 2 * sum_even + y[-1])

    if not silent:
        log(f"  Suma y_impar (y₁, y₃...): {sum_odd:.4f}", "calc")
        log(f"  Suma y_par (y₂, y₄...): {sum_even:.4f}", "calc")
        log(f"  I = ({h}/3) * ({y[0]} + 4*({sum_odd:.4f}) + 2*({sum_even:.4f}) + {y[-1]})", "calc")
        log(f"\nResultado (Simpson 1/3):", "title")
        log(f"  Integral ≈ {I:.8f}", "solution")
    return I


def solve_simpson38(x, y, h, N, log, silent=False):
    """Calcula la integral usando Simpson 3/8 (Compuesto). Asume N es múltiplo de 3."""
    if not silent:
        log("Fórmula: (3h/8) * [y₀ + 3*Σ(y_i) + 2*Σ(y_m3) + yₙ]", "calc")

    sum_1 = 0  # Para y₁, y₄, y₇...
    sum_2 = 0  # Para y₂, y₅, y₈...
    sum_3 = 0  # Para y₃, y₆, y₉... (múltiplos de 3)

    for i in range(1, N):
        if i % 3 == 0:
            sum_3 += y[i]
        elif i % 3 == 1:
            sum_1 += y[i]
        else:  # i % 3 == 2
            sum_2 += y[i]

    I = (3 * h / 8) * (y[0] + 3 * sum_1 + 3 * sum_2 + 2 * sum_3 + y[-1])

    if not silent:
        log(f"  Suma y_i (i%3=1): {sum_1:.4f}", "calc")
        log(f"  Suma y_i (i%3=2): {sum_2:.4f}", "calc")
        log(f"  Suma y_i (i%3=0): {sum_3:.4f}", "calc")
        log(f"  I = (3*{h}/8) * ({y[0]} + 3*({sum_1:.4f}) + 3*({sum_2:.4f}) + 2*({sum_3:.4f}) + {y[-1]})", "calc")
        log(f"\nResultado (Simpson 3/8):", "title")
        log(f"  Integral ≈ {I:.8f}", "solution")
    return I


# --- Método Automático ---
def solve_automatic(x, y, h, N, log):
    """
    Selecciona el mejor método o combinación de métodos basado
    en el número de segmentos (N).
    """
    log("Iniciando Modo Automático", "title")
    log(f"Analizando {N} segmentos...", "step")

    if N == 1:
        log("N=1. Usando Regla del Trapecio (Simple).", "step")
        I = solve_trapecio(x, y, h, N, log, silent=True)  # Llamada silenciosa
        log(f"  I = ({h}/2) * ({y[0]} + {y[1]}) = {I:.8f}", "calc")

    elif N % 2 == 0:
        # N es par. El mejor método es Simpson 1/3
        log(f"N={N} (par). Usando Regla de Simpson 1/3.", "step")
        I = solve_simpson13(x, y, h, N, log)  # Llamada normal con log

    elif N % 3 == 0:
        # N es impar pero múltiplo de 3
        log(f"N={N} (múltiplo de 3). Usando Regla de Simpson 3/8.", "step")
        I = solve_simpson38(x, y, h, N, log)  # Llamada normal con log

    else:
        # N es impar y no múltiplo de 3
        # Este es el caso de COMBINACIÓN.
        # Usamos Simpson 1/3 en los primeros N-3 segmentos y Simpson 3/8 en los últimos 3 segmentos.
        log(f"N={N} (impar, no múltiplo de 3).", "warn")
        log("Aplicando combinación:", "step")
        log(f"  -> Simpson 1/3 (primeros {N - 3} segmentos)", "step")
        log(f"  -> Simpson 3/8 (últimos 3 segmentos)", "step")

        # Simpson 1/3 en x[0]...x[N-3]
        x_s13 = x[:(N - 3) + 1]  # +1 porque Slicing no incluye el último
        y_s13 = y[:(N - 3) + 1]
        I_s13 = solve_simpson13(x_s13, y_s13, h, N - 3, log, silent=True)
        log(f"  Integral (Simpson 1/3) = {I_s13:.8f}", "calc")

        # Simpson 3/8 en x[N-3]...x[N]
        x_s38 = x[N - 3:]
        y_s38 = y[N - 3:]
        I_s38 = solve_simpson38(x_s38, y_s38, h, 3, log, silent=True)
        log(f"  Integral (Simpson 3/8) = {I_s38:.8f}", "calc")

        I = I_s13 + I_s38
        log(f"  Suma = {I_s13:.8f} + {I_s38:.8f}", "calc")

    log(f"\nResultado (Automático):", "title")
    log(f"  Integral Total ≈ {I:.8f}", "solution")