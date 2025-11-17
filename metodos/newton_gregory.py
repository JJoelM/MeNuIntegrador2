import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import math

# Lista para mantener referencia a los widgets Entry de los puntos
points_entries = []


def create_newton_frame(parent_frame):
    """Crea la UI para el método de Newton-Gregory."""

    # --- Variables de control ---
    n_var = ttk.IntVar(value=4)  # Número de puntos
    method_var = ttk.StringVar(value="forward")  # 'forward' o 'backward'

    # --- Frames de UI ---
    # Controles (N Puntos, Valor X a interpolar)
    input_frame = ttk.Frame(parent_frame)
    input_frame.pack(fill=X, pady=5)

    # Tabla de puntos (xi, yi)
    points_frame = ttk.Frame(parent_frame)
    points_frame.pack(fill=X, pady=10)

    # Selector de método y botón de cálculo
    controls_frame = ttk.Frame(parent_frame)
    controls_frame.pack(fill=X, pady=5)

    # Resultados
    results_frame = ttk.Labelframe(parent_frame, text="Resultados (Paso a Paso)", padding=10)
    results_frame.pack(fill=BOTH, expand=YES, pady=5)

    # --- Controles de Entrada ---
    ttk.Label(input_frame, text="Número de Puntos (n):").pack(side=LEFT, padx=5)
    n_spinbox = ttk.Spinbox(input_frame, from_=3, to=10, textvariable=n_var, width=5)
    n_spinbox.pack(side=LEFT, padx=5)

    ttk.Label(input_frame, text="Valor de X a interpolar:").pack(side=LEFT, padx=15)
    x_target_entry = ttk.Entry(input_frame, width=10)
    x_target_entry.pack(side=LEFT, padx=5)

    create_btn = ttk.Button(
        input_frame,
        text="Generar Tabla",
        command=lambda: generate_points_grid(n_var.get(), points_frame),
    )
    create_btn.pack(side=RIGHT, padx=10)

    # --- Selector de Método y Cálculo ---
    fwd_radio = ttk.Radiobutton(controls_frame, text="Ascendente (Forward)", variable=method_var, value="forward")
    fwd_radio.pack(side=LEFT, padx=10)

    bwd_radio = ttk.Radiobutton(controls_frame, text="Descendente (Backward)", variable=method_var, value="backward")
    bwd_radio.pack(side=LEFT, padx=10)

    solve_btn = ttk.Button(
        controls_frame,
        text="Interpolar y Derivar",  # Texto del botón actualizado
        command=lambda: solve_newton_gregory(
            n_var, x_target_entry, method_var, results_text
        ),
        bootstyle=SUCCESS
    )
    solve_btn.pack(side=RIGHT, padx=20)

    # --- Resultados ---
    results_text = ScrolledText(results_frame, width=70, height=20, state="disabled", wrap="word")
    results_text.pack(fill=BOTH, expand=YES)

    # Etiquetas de Salita
    results_text.tag_config("title", font=("Helvetica", 14, "bold"), foreground="blue")
    results_text.tag_config("step", font=("Courier", 12, "italic"), foreground="gray")
    results_text.tag_config("table", font=("Courier", 11))
    results_text.tag_config("calc", font=("Courier", 12))
    results_text.tag_config("solution", font=("Helvetica", 12, "bold"), foreground="green")
    results_text.tag_config("error", font=("Helvetica", 12, "bold"), foreground="red")
    results_text.tag_config("deriv", font=("Helvetica", 12, "bold"), foreground="purple")

    # Tabla de puntos inicial
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
        # Etiqueta de Fila
        row_label = ttk.Label(frame, text=f"P{i}")
        row_label.grid(row=i + 1, column=0, padx=5, sticky="e")

        # Entradas
        entry_x = ttk.Entry(frame, width=15, justify="center")
        entry_x.grid(row=i + 1, column=1, padx=5, pady=5)

        entry_y = ttk.Entry(frame, width=15, justify="center")
        entry_y.grid(row=i + 1, column=2, padx=5, pady=5)

        points_entries.append((entry_x, entry_y))

    # Peso de las columnas
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=2)
    frame.grid_columnconfigure(2, weight=2)


def solve_newton_gregory(n_var, x_target_entry, method_var, results_text):
    """Punto de entrada: Valida y llama a la lógica de interpolación y derivación."""
    global points_entries
    h = 0.0  # Se inicializa aquí

    # --- UI resultados ---
    results_text.config(state="normal")
    results_text.delete("1.0", END)

    def log(message, tag=None):
        if tag:
            results_text.insert(END, message + "\n", tag)
        else:
            results_text.insert(END, message + "\n")
        results_text.see(END)
        results_text.update_idletasks()

    # --- Validación de entradas ---
    try:
        n = n_var.get()
        x_target = float(x_target_entry.get())
        method = method_var.get()

        x_values = []
        y_values = []

        if len(points_entries) != n:
            log("Error: El número de puntos no coincide. Presiona 'Generar Tabla' de nuevo.", "error")
            return

        for i, (entry_x, entry_y) in enumerate(points_entries):
            val_x = entry_x.get()
            val_y = entry_y.get()
            if not val_x or not val_y:
                raise ValueError(f"El punto P{i} está vacío.")
            x_values.append(float(val_x))
            y_values.append(float(val_y))

        # --- Validación: Equidistancia h ---
        if n > 1:
            # Asignamos a la variable 'h' definida fuera del try
            h = np.round(x_values[1] - x_values[0], 9)  # Calcular h inicial
            if h <= 0:
                raise ValueError("Los valores de X deben ser crecientes.")

            for i in range(1, n - 1):
                h_i = np.round(x_values[i + 1] - x_values[i], 9)
                if not np.isclose(h, h_i):
                    log(f"Error: Los valores de X NO son equidistantes.", "error")
                    log(f"  h entre P0 y P1 = {h}", "error")
                    log(f"  h entre P{i} y P{i + 1} = {h_i}", "error")
                    return
        else:
            h = 1  # Valor por defecto

        log(f"Validación exitosa: Puntos equidistantes con h = {h}\n", "step")

    except ValueError as e:
        log(f"Error de Entrada: {e}", "error")
        results_text.config(state="disabled")  # Bloquear al fallar
        return
    except Exception as e:
        log(f"Error inesperado: {e}", "error")
        results_text.config(state="disabled")  # Bloquear al fallar
        return

    # --- Bloque de Cálculo ---
    try:
        if method == "forward":
            log("Iniciando Interpolación de Newton-Gregory (Ascendente)", "title")
            table = build_forward_diff_table(y_values, n)
            log("\nTabla de Diferencias Finitas (Ascendente Δ):", "step")
            log(format_diff_table(x_values, y_values, table, n, backward=False), "table")

            # Calcular u
            u = (x_target - x_values[0]) / h
            log(f"\nCálculo de 'u' (para x = {x_target}):", "step")
            log(f"  u = (x - x₀) / h = ({x_target} - {x_values[0]}) / {h}", "calc")
            log(f"  u = {u:.6f}\n", "calc")

            # Aplicar la fórmula de interpolación
            diffs_y0 = table[0, :]  # La primera fila contiene y₀, Δy₀, Δ2y₀, ...
            result = apply_newton_forward(diffs_y0, u, n, log)
            log(f"\nResultado Interpolación:", "title")
            log(f"  P({x_target}) ≈ {result:.8f}", "solution")

            # --- Cálculo de Derivadas ---
            log("\n--- Cálculo de Derivadas (Ascendente) ---", "title")
            apply_newton_derivatives(diffs_y0, u, n, h, log, x_target, backward=False)

        else:  # method == "backward"
            log("Iniciando Interpolación de Newton-Gregory (Descendente)", "title")
            table = build_backward_diff_table(y_values, n)
            log("\nTabla de Diferencias Finitas (Descendente ∇):", "step")
            log(format_diff_table(x_values, y_values, table, n, backward=True), "table")

            # Calcular u
            u = (x_target - x_values[-1]) / h
            log(f"\nCálculo de 'u' (para x = {x_target}):", "step")
            log(f"  u = (x - xₙ) / h = ({x_target} - {x_values[-1]}) / {h}", "calc")
            log(f"  u = {u:.6f}\n", "calc")

            # Aplicar la fórmula de interpolación
            diffs_yn = table[-1, :]  # La última fila contiene yₙ, ∇yₙ, ∇2yₙ, ...
            result = apply_newton_backward(diffs_yn, u, n, log)
            log(f"\nResultado Interpolación:", "title")
            log(f"  P({x_target}) ≈ {result:.8f}", "solution")

            # --- Cálculo de Derivadas ---
            log("\n--- Cálculo de Derivadas (Descendente) ---", "title")
            apply_newton_derivatives(diffs_yn, u, n, h, log, x_target, backward=True)

    except Exception as e:
        log(f"\nError durante el cálculo: {e}", "error")
    finally:
        results_text.config(state="disabled")  # Bloquear siempre al final


def build_forward_diff_table(y, n):
    """Construye la tabla de diferencias ascendente."""
    table = np.zeros((n, n))
    table[:, 0] = y  # Columna 0 es f(x_i)

    for j in range(1, n):  # Columna (Orden de la diferencia)
        for i in range(0, n - j):  # Fila
            table[i, j] = table[i + 1, j - 1] - table[i, j - 1]
    return table


def build_backward_diff_table(y, n):
    """Construye la tabla de diferencias descendente."""
    table = np.zeros((n, n))
    table[:, 0] = y  # Columna 0 es f(x_i)

    for j in range(1, n):  # Columna (Orden de la diferencia)
        for i in range(j, n):  # Fila
            table[i, j] = table[i, j - 1] - table[i - 1, j - 1]
    return table


def format_diff_table(x, y, table, n, backward=False):
    """Formatea la tabla de diferencias para una salida estética."""
    symbol = "Δ" if not backward else "∇"

    # Cabecera
    headers = ["x_i", "y_i"] + [f"{symbol}^{j}y" for j in range(1, n)]
    header_str = " | ".join([f"{h:^10}" for h in headers])
    lines = [header_str, "-" * len(header_str)]

    # Filas
    for i in range(n):
        row = [f"{x[i]:^10.4f}", f"{y[i]:^10.4f}"]
        for j in range(1, n):
            if (not backward and i + j < n) or (backward and i >= j):
                val = table[i, j]
                # No mostrar ceros que son solo relleno de numpy
                val_str = f"{val:^10.4f}" if not np.isclose(val, 0) or (i == 0 and j == 0) else " " * 10

                # Ocultar valores irrelevantes para la forma del triángulo
                if not backward and i + j >= n:
                    val_str = " " * 10
                if backward and i < j:
                    val_str = " " * 10

                row.append(val_str)
            else:
                row.append(" " * 10)

        # Recortar espacios vacíos al final
        while row and row[-1].strip() == "":
            row.pop()

        lines.append(" | ".join(row))

    return "\n".join(lines)


def apply_newton_forward(diffs_y0, s, n, log_callback):
    """Aplica la fórmula ascendente paso a paso."""
    log_callback("Aplicando Fórmula Ascendente P(x) = y₀ + sΔy₀ + s(s-1)/2! Δ²y₀ + ...", "step")

    result = diffs_y0[0]
    term_s = 1.0

    log_callback(f"  Término 0 (y₀): {result:.6f}", "calc")

    for i in range(1, n):
        if np.isclose(diffs_y0[i], 0):
            log_callback(f"  Término {i}: 0 (Diferencia nula)", "calc")
            continue

        term_s = term_s * (s - (i - 1))
        factorial_i = math.factorial(i)

        current_term_value = (term_s / factorial_i) * diffs_y0[i]
        result += current_term_value

        log_callback(f"  Término {i}: (s-0)..({s - (i - 1)})/{i}! * {diffs_y0[i]:.4f} = {current_term_value:.6f}",
                     "calc")

    return result


def apply_newton_backward(diffs_yn, s, n, log_callback):
    """Aplica la fórmula descendente paso a paso."""
    log_callback("Aplicando Fórmula Descendente P(x) = yₙ + s∇yₙ + s(s+1)/2! ∇²yₙ + ...", "step")

    result = diffs_yn[0]
    term_s = 1.0

    log_callback(f"  Término 0 (yₙ): {result:.6f}", "calc")

    for i in range(1, n):
        if np.isclose(diffs_yn[i], 0):
            log_callback(f"  Término {i}: 0 (Diferencia nula)", "calc")
            continue

        term_s = term_s * (s + (i - 1))
        factorial_i = math.factorial(i)

        current_term_value = (term_s / factorial_i) * diffs_yn[i]
        result += current_term_value

        log_callback(f"  Término {i}: (s+0)..({s + (i - 1)})/{i}! * {diffs_yn[i]:.4f} = {current_term_value:.6f}",
                     "calc")

    return result


# --- DERIVADAS ---
# Me había olvidado que esto también iba
def _get_s_poly_derivs_forward(i, s):
    """
    Calcula la 1ra (p') y 2da (p'') derivada del polinomio 's' ascendente
    p_i(s) = s(s-1)...(s-i+1)
    Retorna (p', p'')
    """
    if i == 0: return (0, 0)
    if i == 1: return (1, 0)
    if i == 2:  # s(s-1) = s^2 - s
        p_prime = 2 * s - 1
        p_double_prime = 2
        return (p_prime, p_double_prime)
    if i == 3:  # s(s-1)(s-2) = s^3 - 3s^2 + 2s
        p_prime = 3 * s ** 2 - 6 * s + 2
        p_double_prime = 6 * s - 6
        return (p_prime, p_double_prime)
    if i == 4:  # s(s-1)(s-2)(s-3) = s^4 - 6s^3 + 11s^2 - 6s
        p_prime = 4 * s ** 3 - 18 * s ** 2 + 22 * s - 6
        p_double_prime = 12 * s ** 2 - 36 * s + 22
        return (p_prime, p_double_prime)
    # Se pueden añadir más términos si se incrementa el N máximo

    # Término genérico (más lento, pero funciona para i > 4)
    # Para la 1ra derivada:
    p_prime = 0
    for j in range(i):
        term_prod = 1
        for k in range(i):
            if k != j:
                term_prod *= (s - k)
        p_prime += term_prod

    # Para la 2da derivada:
    p_double_prime = 0
    for j in range(i):
        for k in range(i):
            if j == k: continue
            term_prod = 1
            for m in range(i):
                if m != j and m != k:
                    term_prod *= (s - m)
            p_double_prime += term_prod

    return (p_prime, p_double_prime)


def _get_s_poly_derivs_backward(i, s):
    """
    Calcula la 1ra (p') y 2da (p'') derivada del polinomio 's' descendente
    p_i(s) = s(s+1)...(s+i-1)
    Retorna (p', p'')
    """
    if i == 0: return (0, 0)
    if i == 1: return (1, 0)
    if i == 2:  # s(s+1) = s^2 + s
        p_prime = 2 * s + 1
        p_double_prime = 2
        return (p_prime, p_double_prime)
    if i == 3:  # s(s+1)(s+2) = s^3 + 3s^2 + 2s
        p_prime = 3 * s ** 2 + 6 * s + 2
        p_double_prime = 6 * s + 6
        return (p_prime, p_double_prime)
    if i == 4:  # s(s+1)(s+2)(s+3) = s^4 + 6s^3 + 11s^2 + 6s
        p_prime = 4 * s ** 3 + 18 * s ** 2 + 22 * s + 6
        p_double_prime = 12 * s ** 2 + 36 * s + 22
        return (p_prime, p_double_prime)

    # Término genérico (más lento, pero funciona para i > 4)
    # Para la 1ra derivada:
    p_prime = 0
    for j in range(i):
        term_prod = 1
        for k in range(i):
            if k != j:
                term_prod *= (s + k)
        p_prime += term_prod

    # Para la 2da derivada:
    p_double_prime = 0
    for j in range(i):
        for k in range(i):
            if j == k: continue
            term_prod = 1
            for m in range(i):
                if m != j and m != k:
                    term_prod *= (s + m)
            p_double_prime += term_prod

    return (p_prime, p_double_prime)


def apply_newton_derivatives(diffs, s, n, h, log_callback, x_target, backward=False):
    """Aplica las fórmulas de derivadas (1ra y 2da) paso a paso."""

    log_callback("\nCálculo de la Primera Derivada f'(x) ≈ (1/h) * Σ [ p'(s)/i! * Δⁱy ]", "step")
    log_callback("Cálculo de la Segunda Derivada f''(x) ≈ (1/h²) * Σ [ p''(s)/i! * Δⁱy ]", "step")

    total_deriv1 = 0.0
    total_deriv2 = 0.0

    for i in range(1, n):  # Empezamos en 1 (el término y0 se anula)
        diff_term = diffs[i]
        if np.isclose(diff_term, 0):
            log_callback(f"  Término {i} (Δ{i}y): 0 (Diferencia nula)", "calc")
            continue

        if backward:
            p_prime, p_double_prime = _get_s_poly_derivs_backward(i, s)
        else:
            p_prime, p_double_prime = _get_s_poly_derivs_forward(i, s)

        factorial_i = math.factorial(i)

        # Cálculo 1ra Derivada
        current_term_d1 = (p_prime / factorial_i) * diff_term
        total_deriv1 += current_term_d1

        # Cálculo 2da Derivada
        current_term_d2 = (p_double_prime / factorial_i) * diff_term
        total_deriv2 += current_term_d2

        log_callback(f"  Término {i}: p'({i},s)={p_prime:.3f}, p''({i},s)={p_double_prime:.3f}", "calc")
        log_callback(f"    f' += {current_term_d1:.6f} | f'' += {current_term_d2:.6f}", "calc")

    # Resultados finales
    final_d1 = (1 / h) * total_deriv1
    final_d2 = (1 / h ** 2) * total_deriv2

    log_callback(f"\nSuma(p'/i! * Δⁱy) = {total_deriv1:.8f}", "calc")
    log_callback(f"Suma(p''/i! * Δⁱy) = {total_deriv2:.8f}", "calc")

    log_callback(f"\nResultado Primera Derivada f'({x_target}):", "deriv")
    log_callback(f"  f'(x) = (1 / {h}) * {total_deriv1:.8f} ≈ {final_d1:.8f}", "solution")

    log_callback(f"\nResultado Segunda Derivada f''({x_target}):", "deriv")
    log_callback(f"  f''(x) = (1 / {h ** 2}) * {total_deriv2:.8f} ≈ {final_d2:.8f}", "solution")

