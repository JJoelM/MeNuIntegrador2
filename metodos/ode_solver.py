import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import sympy as sp
import math

# --- Variables globales para sympy ---
x_sym, y_sym = sp.symbols('x y')
# Lista de funciones para sympify
safe_sympy_funcs = {
    'exp': sp.exp,
    'sin': sp.sin,
    'cos': sp.cos,
    'tan': sp.tan,
    'sqrt': sp.sqrt,
    'log': sp.log,
    'pi': sp.pi
}


def create_ode_frame(parent_frame):
    """Crea la UI para el módulo de Ecuaciones Diferenciales Ordinarias (EDO)."""

    # --- Frames de UI ---
    main_container = ttk.Frame(parent_frame)
    main_container.pack(fill=BOTH, expand=YES)

    input_frame = ttk.Labelframe(main_container, text="Entradas del Problema", padding=10)
    input_frame.pack(fill=X, padx=10, pady=5)

    method_frame = ttk.Labelframe(main_container, text="Selección del Método", padding=10)
    method_frame.pack(fill=X, padx=10, pady=5)

    # --- Frame de Resultados Dividido ---
    results_frame = ttk.Labelframe(main_container, text="Resultados", padding=10)
    results_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    # Tabla Treeview (Resultados finales o  resumen)
    tree_frame = ttk.Frame(results_frame)
    tree_frame.pack(fill=X, pady=5)

    # Log ScrolledText (Paso a Paso)
    log_frame = ttk.Frame(results_frame)
    log_frame.pack(fill=BOTH, expand=YES, pady=5)

    # --- Entradas del Problema ---
    ttk.Label(input_frame, text="EDO y' = f(x, y):", width=18).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    f_entry = ttk.Entry(input_frame, width=30)
    f_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    f_entry.insert(0, "x**2 + y**2")  # Ejemplo de la guía

    ttk.Label(input_frame, text="Solución Real y(x):", width=18).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    y_real_entry = ttk.Entry(input_frame, width=30)
    y_real_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    y_real_entry.insert(0, "")  # Dejar vacío si no se conoce

    ttk.Label(input_frame, text="x₀:", width=5).grid(row=0, column=2, padx=5, pady=5, sticky="e")
    x0_entry = ttk.Entry(input_frame, width=8)
    x0_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    x0_entry.insert(0, "0")

    ttk.Label(input_frame, text="y₀:", width=5).grid(row=1, column=2, padx=5, pady=5, sticky="e")
    y0_entry = ttk.Entry(input_frame, width=8)
    y0_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
    y0_entry.insert(0, "1")  # Ejemplo de la guía

    ttk.Label(input_frame, text="h:", width=5).grid(row=0, column=4, padx=5, pady=5, sticky="e")
    h_entry = ttk.Entry(input_frame, width=8)
    h_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")
    h_entry.insert(0, "0.2")

    ttk.Label(input_frame, text="x final:", width=5).grid(row=1, column=4, padx=5, pady=5, sticky="e")
    xf_entry = ttk.Entry(input_frame, width=8)
    xf_entry.grid(row=1, column=5, padx=5, pady=5, sticky="w")
    xf_entry.insert(0, "0.6")

    input_frame.columnconfigure(1, weight=1)

    # --- Selección del Método ---
    method_var = ttk.StringVar(value="Euler Modificado")
    startup_var = ttk.StringVar(value="RK4")

    method_options = ["Euler", "Euler Modificado", "RK2 (Punto Medio)", "RK4", "Milne (Predictor-Corrector)"]
    startup_options = ["Euler Modificado", "RK2 (Punto Medio)", "RK4"]

    ttk.Label(method_frame, text="Método Principal:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    main_method_combo = ttk.Combobox(method_frame, textvariable=method_var, values=method_options, width=30,
                                     state="readonly")
    main_method_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(method_frame, text="Método de Arranque (p/ Milne):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    startup_method_combo = ttk.Combobox(method_frame, textvariable=startup_var, values=startup_options, width=30,
                                        state="disabled")
    startup_method_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tol_label = ttk.Label(method_frame, text="Tolerancia E (p/ Euler Mod):")
    tol_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    tol_entry = ttk.Entry(method_frame, width=15, state="disabled")
    tol_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    tol_entry.insert(0, "0.0000001")

    def on_main_method_select(event):
        main_method = method_var.get()
        if main_method == "Milne (Predictor-Corrector)":
            startup_method_combo.config(state="readonly")
            if not startup_var.get(): startup_var.set("RK4")
        else:
            startup_method_combo.config(state="disabled")

        if main_method == "Euler Modificado":
            tol_label.config(bootstyle="default")
            tol_entry.config(state="normal")
        else:
            tol_label.config(bootstyle="secondary")
            tol_entry.config(state="disabled")

    main_method_combo.bind("<<ComboboxSelected>>", on_main_method_select)
    on_main_method_select(None)

    # --- Resultados (Treeview) ---
    tree_cols = ("i", "x", "y_calc", "y_real", "error")
    results_tree = ttk.Treeview(tree_frame, columns=tree_cols, show="headings", height=6)

    results_tree.heading("i", text="Paso (i)")
    results_tree.heading("x", text="xᵢ")
    results_tree.heading("y_calc", text="yᵢ (Calculado)")
    results_tree.heading("y_real", text="yᵢ (Real)")
    results_tree.heading("error", text="Error %")

    results_tree.column("i", width=60, anchor="center")
    results_tree.column("x", width=100, anchor="e")
    results_tree.column("y_calc", width=150, anchor="e")
    results_tree.column("y_real", width=150, anchor="e")
    results_tree.column("error", width=100, anchor="e")

    tree_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=results_tree.yview)
    results_tree.configure(yscrollcommand=tree_scrollbar.set)
    tree_scrollbar.pack(side=RIGHT, fill=Y)
    results_tree.pack(fill=BOTH, expand=YES)

    # --- Resultados (Log) ---
    ttk.Label(log_frame, text="Log de Cálculo (Paso a Paso):").pack(fill=X)
    log_text = ScrolledText(log_frame, width=70, height=10, state="disabled", wrap="word", font=("Courier New", 9))
    log_text.pack(fill=BOTH, expand=YES)

    solve_btn = ttk.Button(
        method_frame,
        text="Calcular Solución",
        command=lambda: solve_ode(
            f_entry, y_real_entry, x0_entry, y0_entry, h_entry, xf_entry,
            method_var, startup_var, tol_entry,
            results_tree, log_text  # <-- Pasamos ambos widgets
        ),
        bootstyle=SUCCESS
    )
    solve_btn.grid(row=0, column=2, rowspan=3, padx=20, pady=5, sticky="ns")
    method_frame.columnconfigure(2, weight=1)


# --- LÓGICA DE PASO ---

def _euler_step(f, x, y, h, log_callback):
    log_callback(f"yᵢ₊₁ = yᵢ + h * f(xᵢ, yᵢ)")
    f_val = f(x, y)
    log_callback(f"yᵢ₊₁ = {y:.6f} + {h} * f({x:.4f}, {y:.6f})")
    log_callback(f"yᵢ₊₁ = {y:.6f} + {h} * {f_val:.6f}")
    y_next = y + h * f_val
    log_callback(f"yᵢ₊₁ = {y_next:.6f}\n")
    return y_next


def _euler_mod_iterative_step(f, x, y, h, tolerance, log_callback, max_iter=100):
    log_callback(f"Predictor (P):")
    f_val = f(x, y)
    log_callback(f"  P = yᵢ + h * f(xᵢ, yᵢ)")
    log_callback(f"  P = {y:.6f} + {h} * f({x:.4f}, {y:.6f}) = {y:.6f} + {h} * {f_val:.6f}")
    y_pred = y + h * f_val
    log_callback(f"  P = {y_pred:.6f}\n")

    y_corr_prev = y_pred

    for i in range(max_iter):
        log_callback(f"Corrector {i + 1} (C^{i + 1}):")
        f_pred = f(x + h, y_corr_prev)
        log_callback(f"  C^{i + 1} = yᵢ + (h/2) * [ f(xᵢ, yᵢ) + f(xᵢ₊₁, C^{i}) ]")
        log_callback(f"  C^{i + 1} = {y:.6f} + ({h / 2}) * [ {f_val:.6f} + f({x + h:.4f}, {y_corr_prev:.6f}) ]")
        log_callback(f"  C^{i + 1} = {y:.6f} + ({h / 2}) * [ {f_val:.6f} + {f_pred:.6f} ]")
        y_corr_new = y + (h / 2) * (f_val + f_pred)
        log_callback(f"  C^{i + 1} = {y_corr_new:.6f}\n")

        error = abs(y_corr_new - y_corr_prev)
        log_callback(f"Error (E):")
        log_callback(f"  E = |C^{i + 1} - C^{i}| = |{y_corr_new:.6f} - {y_corr_prev:.6f}| = {error:.6E}")

        if error < tolerance:
            log_callback(f"  (E < {tolerance:.0E}. Convergencia alcanzada.)\n")
            return y_corr_new

        y_corr_prev = y_corr_new
        log_callback(f"  (E > {tolerance:.0E}. Iterando...)\n")

    raise RuntimeError(f"Euler Modificado no convergió en x={x} (max_iter={max_iter} alcanzado)")


def _rk2_midpoint_step(f, x, y, h, log_callback):
    log_callback(f"k₁ = f(xᵢ, yᵢ) = f({x:.4f}, {y:.6f})")
    k1 = f(x, y)
    log_callback(f"k₁ = {k1:.6f}\n")

    log_callback(f"k₂ = f(xᵢ+h/2, yᵢ+h*k₁/2)")
    log_callback(f"k₂ = f({x + h / 2:.4f}, {y + (h / 2) * k1:.6f})")
    k2 = f(x + h / 2, y + (h / 2) * k1)
    log_callback(f"k₂ = {k2:.6f}\n")

    log_callback(f"yᵢ₊₁ = yᵢ + h * k₂")
    y_next = y + h * k2
    log_callback(f"yᵢ₊₁ = {y:.6f} + {h} * {k2:.6f} = {y_next:.6f}\n")
    return y_next


def _rk4_step(f, x, y, h, log_callback):
    log_callback(f"k₁ = f(xᵢ, yᵢ) = f({x:.4f}, {y:.6f})")
    k1 = f(x, y)
    log_callback(f"k₁ = {k1:.6f}\n")

    log_callback(f"k₂ = f(xᵢ+h/2, yᵢ+h*k₁/2)")
    log_callback(f"k₂ = f({x + h / 2:.4f}, {y + (h / 2) * k1:.6f})")
    k2 = f(x + h / 2, y + (h / 2) * k1)
    log_callback(f"k₂ = {k2:.6f}\n")

    log_callback(f"k₃ = f(xᵢ+h/2, yᵢ+h*k₂/2)")
    log_callback(f"k₃ = f({x + h / 2:.4f}, {y + (h / 2) * k2:.6f})")
    k3 = f(x + h / 2, y + (h / 2) * k2)
    log_callback(f"k₃ = {k3:.6f}\n")

    log_callback(f"k₄ = f(xᵢ+h, yᵢ+h*k₃)")
    log_callback(f"k₄ = f({x + h:.4f}, {y + h * k3:.6f})")
    k4 = f(x + h, y + h * k3)
    log_callback(f"k₄ = {k4:.6f}\n")

    log_callback(f"yᵢ₊₁ = yᵢ + (h/6) * (k₁ + 2k₂ + 2k₃ + k₄)")
    y_next = y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    log_callback(f"yᵢ₊₁ = {y:.6f} + ({h / 6:.4f}) * ({k1:.6f} + 2*{k2:.6f} + 2*{k3:.6f} + {k4:.6f})")
    log_callback(f"yᵢ₊₁ = {y_next:.6f}\n")
    return y_next


# --- LÓGICA PRINCIPAL DE SOLUCIÓN ---

def solve_ode(f_entry, y_real_entry, x0_entry, y0_entry, h_entry, xf_entry,
              method_var, startup_var, tol_entry,
              results_tree, log_text):  # <-- Recibimos el log_text

    # --- Limpiar UI ---
    results_tree.delete(*results_tree.get_children())
    log_text.config(state="normal")
    log_text.delete("1.0", END)

    # --- Helper para el Log ---
    def log_callback(message):
        log_text.insert(END, message + "\n")
        log_text.see(END)

    # --- Validar Entradas Numéricas ---
    try:
        x0 = float(x0_entry.get())
        y0 = float(y0_entry.get())
        h = float(h_entry.get())
        xf = float(xf_entry.get())

        tolerance = float(tol_entry.get()) if tol_entry.cget("state") == "normal" else 0.001

        if h <= 0: raise ValueError("h debe ser positivo")
        if xf <= x0: raise ValueError("x final debe ser mayor que x₀")
        if tolerance <= 0: raise ValueError("Tolerancia E debe ser positiva")

    except ValueError as e:
        Messagebox.show_error("Error de Entrada", f"Valor numérico inválido: {e}")
        log_text.config(state="disabled")
        return

    # --- Compilar Funciones SymPy ---
    try:
        f_text = f_entry.get()
        f_expr = sp.sympify(f_text, locals=safe_sympy_funcs)
        f_func = sp.lambdify((x_sym, y_sym), f_expr, 'numpy')
        f_func(x0, y0)

    except Exception as e:
        Messagebox.show_error("Error de Ecuación", f"Error en la EDO f(x, y):\n{e}")
        log_text.config(state="disabled")
        return

    try:
        y_real_text = y_real_entry.get()
        y_real_func = None
        if y_real_text.strip():
            y_real_expr = sp.sympify(y_real_text, locals=safe_sympy_funcs)
            y_real_func = sp.lambdify(x_sym, y_real_expr, 'numpy')
            y_real_func(x0)

    except Exception as e:
        Messagebox.show_error("Error de Ecuación", f"Error en la Solución Real y(x):\n{e}")
        log_text.config(state="disabled")
        return

    # --- Preparar Cálculo ---
    main_method = method_var.get()
    startup_method = startup_var.get()

    x_points = np.arange(x0, xf + h * 0.5, h)
    n_steps = len(x_points)

    y_points = np.zeros(n_steps)
    y_points[0] = y0

    # --- Función para poblar la tabla ---
    def add_to_tree(i, x, y_calc):
        yi_real_str = "---"
        error_str = "---"
        if y_real_func:
            try:
                yi_real = y_real_func(x)
                yi_real_str = f"{yi_real:.8f}"
                if abs(yi_real) > 1e-10:
                    error = abs((yi_real - y_calc) / yi_real) * 100
                    error_str = f"{error:.4f} %"
                else:
                    error_str = "N/A (y_real=0)"
            except Exception:
                yi_real_str = "Error"
                error_str = "Error"
        results_tree.insert("", "end", values=(i, f"{x:.4f}", f"{y_calc:.8f}", yi_real_str, error_str))

    # --- Enviar al Método de Solución ---

    try:
        log_callback(f"Iniciando cálculo con Método: {main_method}")
        log_callback(f"Parámetros: x₀={x0}, y₀={y0}, h={h}, x_final={xf}\n")
        add_to_tree(0, x0, y0)  # Añadir el punto inicial

        # --- Métodos de un solo paso ---
        if main_method == "Euler":
            for i in range(n_steps - 1):
                log_callback(f"--- Paso {i + 1} (x = {x_points[i]:.4f} -> {x_points[i + 1]:.4f}) ---")
                y_next = _euler_step(f_func, x_points[i], y_points[i], h, log_callback)
                y_points[i + 1] = y_next
                add_to_tree(i + 1, x_points[i + 1], y_next)

        elif main_method == "Euler Modificado":
            for i in range(n_steps - 1):
                log_callback(f"--- Paso {i + 1} (x = {x_points[i]:.4f} -> {x_points[i + 1]:.4f}) ---")
                y_next = _euler_mod_iterative_step(f_func, x_points[i], y_points[i], h, tolerance, log_callback)
                y_points[i + 1] = y_next
                add_to_tree(i + 1, x_points[i + 1], y_next)

        elif main_method == "RK2 (Punto Medio)":
            for i in range(n_steps - 1):
                log_callback(f"--- Paso {i + 1} (x = {x_points[i]:.4f} -> {x_points[i + 1]:.4f}) ---")
                y_next = _rk2_midpoint_step(f_func, x_points[i], y_points[i], h, log_callback)
                y_points[i + 1] = y_next
                add_to_tree(i + 1, x_points[i + 1], y_next)

        elif main_method == "RK4":
            for i in range(n_steps - 1):
                log_callback(f"--- Paso {i + 1} (x = {x_points[i]:.4f} -> {x_points[i + 1]:.4f}) ---")
                y_next = _rk4_step(f_func, x_points[i], y_points[i], h, log_callback)
                y_points[i + 1] = y_next
                add_to_tree(i + 1, x_points[i + 1], y_next)

        # --- Método Multi-Paso (Milne) ---
        elif main_method == "Milne (Predictor-Corrector)":
            if n_steps < 5:
                raise ValueError("Milne requiere al menos 5 puntos (4 pasos). Aumenta 'x final' o disminuye 'h'.")

            log_callback(f"Método de Milne seleccionado.")
            log_callback(f"Usando {startup_method} para los primeros 3 pasos de arranque.\n")

            # Calcular los primeros 3 puntos (y₁, y₂, y₃) con el método de arranque
            if startup_method == "Euler Modificado":
                step_func = lambda x, y, h, log: _euler_mod_iterative_step(f_func, x, y, h, tolerance, log)
            elif startup_method == "RK2 (Punto Medio)":
                step_func = lambda x, y, h, log: _rk2_midpoint_step(f_func, x, y, h, log)
            else:  # RK4
                step_func = lambda x, y, h, log: _rk4_step(f_func, x, y, h, log)

            for i in range(3):
                log_callback(f"--- Paso de Arranque {i + 1} (x = {x_points[i]:.4f} -> {x_points[i + 1]:.4f}) ---")
                y_next = step_func(x_points[i], y_points[i], h, log_callback)
                y_points[i + 1] = y_next
                add_to_tree(i + 1, x_points[i + 1], y_next)

            log_callback("\n--- Arranque completado. Iniciando Milne P-C ---")

            # Aplicar Milne para i = 4 hasta el final
            f_vals = [f_func(x_points[i], y_points[i]) for i in range(4)]

            for i in range(3, n_steps - 1):
                log_callback(f"--- Paso {i + 1} (x = {x_points[i]:.4f} -> {x_points[i + 1]:.4f}) ---")

                # Predictor (P)
                log_callback(f"Predictor (P):")
                log_callback(f"  Pᵢ₊₁ = yᵢ₋₃ + (4h/3) * [ 2fᵢ₋₂ - fᵢ₋₁ + 2fᵢ ]")
                log_callback(
                    f"  Pᵢ₊₁ = {y_points[i - 3]:.6f} + ({4 * h / 3:.4f}) * [ 2*{f_vals[i - 2]:.6f} - {f_vals[i - 1]:.6f} + 2*{f_vals[i]:.6f} ]")
                y_pred = y_points[i - 3] + (4 * h / 3) * (2 * f_vals[i - 2] - f_vals[i - 1] + 2 * f_vals[i])
                log_callback(f"  Pᵢ₊₁ = {y_pred:.6f}\n")

                f_pred = f_func(x_points[i + 1], y_pred)

                # Corrector (C)
                log_callback(f"Corrector (C):")
                log_callback(f"  Cᵢ₊₁ = yᵢ₋₁ + (h/3) * [ fᵢ₋₁ + 4fᵢ + f_predicha ]")
                log_callback(
                    f"  Cᵢ₊₁ = {y_points[i - 1]:.6f} + ({h / 3:.4f}) * [ {f_vals[i - 1]:.6f} + 4*{f_vals[i]:.6f} + {f_pred:.6f} ]")
                y_corr = y_points[i - 1] + (h / 3) * (f_vals[i - 1] + 4 * f_vals[i] + f_pred)
                log_callback(f"  Cᵢ₊₁ = {y_corr:.6f}\n")

                y_points[i + 1] = y_corr
                f_vals.append(f_func(x_points[i + 1], y_corr))
                add_to_tree(i + 1, x_points[i + 1], y_corr)

    except Exception as e:
        Messagebox.show_error("Error de Cálculo", f"Ocurrió un error durante la simulación:\n{e}")

    finally:
        # Siempre bloquear el log al final
        log_text.config(state="disabled")

