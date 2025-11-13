import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np


def create_gauss_frame(parent_frame):
    """Crea la UI para el método de Eliminación Gaussiana."""

    # --- Variables de control ---
    # Lista para mantener referencia a los widgets Entry de la matriz
    matrix_entries = []

    # --- Frames de UI ---
    # Controles de entrada (tamaño de matriz)
    input_frame = ttk.Frame(parent_frame)
    input_frame.pack(fill=X, pady=5)

    # Matriz dinámica
    matrix_frame = ttk.Frame(parent_frame)
    matrix_frame.pack(fill=X, pady=10)

    # Resultados (paso a paso)
    results_frame = ttk.Labelframe(parent_frame, text="Resultados (Paso a Paso)", padding=10)
    results_frame.pack(fill=BOTH, expand=YES, pady=5)

    # --- Controles de Entrada ---
    ttk.Label(input_frame, text="Tamaño del sistema (n):").pack(side=LEFT, padx=5)

    # Spinbox para seleccionar el tamaño n (de 2x2 a 8x8)
    n_var = ttk.IntVar(value=3)
    n_spinbox = ttk.Spinbox(input_frame, from_=2, to=8, textvariable=n_var, width=5)
    n_spinbox.pack(side=LEFT, padx=5)

    create_btn = ttk.Button(
        input_frame,
        text="Generar Matriz",
        command=lambda: generate_matrix_grid(n_var.get(), matrix_frame, matrix_entries),
        bootstyle=SECONDARY
    )
    create_btn.pack(side=LEFT, padx=10)

    solve_btn = ttk.Button(
        input_frame,
        text="Resolver Sistema",
        command=lambda: solve_system(n_var.get(), matrix_entries, results_text),
        bootstyle=SUCCESS
    )
    solve_btn.pack(side=RIGHT, padx=10)

    # --- Área de Resultados ---
    results_text = ScrolledText(results_frame, width=70, height=20, state="disabled", wrap="word")
    results_text.pack(fill=BOTH, expand=YES)

    # Generar la matriz inicial (ej. 3x3)
    generate_matrix_grid(n_var.get(), matrix_frame, matrix_entries)


def generate_matrix_grid(n, frame, entries_list):
    """Genera dinámicamente la cuadrícula de Entradas para la matriz."""
    for widget in frame.winfo_children():
        widget.destroy()
    entries_list.clear()

    # n = número de ecuaciones
    # n+1 = número de columnas (incluyendo el vector de resultados)

    # --- Añadir cabeceras ---
    for j in range(n + 1):
        style = "secondary.TLabel"
        if j < n:
            label_text = f"x{j + 1}"
        else:
            label_text = "b"
            style = "primary.TLabel"  # Resaltar el vector de resultados

        header = ttk.Label(frame, text=label_text, bootstyle=style, anchor="center")
        header.grid(row=0, column=j + 1, padx=5, pady=2, sticky="ew")  # j+1 para dejar espacio a Fila N

    # --- Matriz de Entradas ---
    for i in range(n):
        # Etiqueta de Fila
        row_label = ttk.Label(frame, text=f"F{i + 1}")
        row_label.grid(row=i + 1, column=0, padx=5, sticky="e")

        row_entries = []
        for j in range(n + 1):
            entry = ttk.Entry(frame, width=8, justify="center")
            entry.grid(row=i + 1, column=j + 1, padx=5, pady=5, sticky="ew")
            row_entries.append(entry)
        entries_list.append(row_entries)

    # Ajustar el peso de las columnas para que se expandan uniformemente
    for j in range(n + 2):  # n+2 (por la etiqueta de fila)
        frame.grid_columnconfigure(j, weight=1)


def solve_system(n, matrix_entries, results_text):
    """Punto de entrada: Valida y llama a la lógica de resolución."""

    # --- Validación de Entradas ---
    try:
        # Convertir los widgets Entry a una matriz de números (float)
        matrix = []
        for i in range(n):
            row = []
            for j in range(n + 1):
                val = matrix_entries[i][j].get()
                if not val:
                    val = 0.0  # Asumir 0 si está vacío
                row.append(float(val))
            matrix.append(row)

        A = np.array(matrix, dtype=float)

    except ValueError:
        Messagebox.show_error("Error de Entrada", "Por favor, introduce solo números válidos en la matriz.")
        return
    except Exception as e:
        Messagebox.show_error("Error", f"Ocurrió un error inesperado: {e}")
        return

    # --- UI de Resultados ---
    results_text.config(state="normal")
    results_text.delete("1.0", END)

    def log(message, tag=None):
        # Función helper para escribir en el ScrolledText
        if tag:
            results_text.insert(END, message + "\n", tag)
        else:
            results_text.insert(END, message + "\n")
        results_text.see(END)  # Auto-scroll
        results_text.update_idletasks()  # Forzar actualización de UI

    # Etiquetas de estilo para la salida
    results_text.tag_config("title", font=("Helvetica", 14, "bold"), foreground="blue")
    results_text.tag_config("step", font=("Courier", 12, "italic"), foreground="gray")
    results_text.tag_config("matrix", font=("Courier", 12))
    results_text.tag_config("solution", font=("Helvetica", 12, "bold"), foreground="green")
    results_text.tag_config("error", font=("Helvetica", 12, "bold"), foreground="red")

    try:
        log("Iniciando Eliminación Gaussiana", "title")
        log("Matriz Aumentada Inicial:", "step")
        log(format_matrix(A), "matrix")


        solution = None
        for step_description in solve_gauss_generator(A, n, log):
            if isinstance(step_description, np.ndarray):
                solution = step_description

        if solution is not None:
            log("\nSolución Encontrada:", "title")
            solution_str = "\n".join([f"  x{i + 1} = {x:.6f}" for i, x in enumerate(solution)])
            log(solution_str, "solution")
        else:
            log("\nNo se pudo encontrar una solución única.", "error")

    except ValueError as e:
        log(f"\nERROR: {e}", "error")

    finally:
        results_text.config(state="disabled")


def format_matrix(M):
    """Helper para imprimir la matriz de forma estética."""
    return str(M)


def solve_gauss_generator(A, n, log_callback):
    """
    Resuelve el sistema Ax=b usando Eliminación Gaussiana.
    Utiliza 'yield' para reportar los pasos intermedios.
    Calcula el determinante para detectar sistemas mal condicionados.
    """

    # --- Variables determinante ---
    determinant = 1.0
    swap_count = 0
    # --------------------------------------

    # Fase de Eliminación (Triangulación)
    for i in range(n):
        # --- Pivoteo (Validación) ---
        if np.abs(A[i, i]) < 1e-10:
            pivot_found = False
            for k in range(i + 1, n):
                if np.abs(A[k, i]) > 1e-10:
                    A[[i, k]] = A[[k, i]]  # Intercambiar filas
                    swap_count += 1  # <-- Contar el intercambio
                    log_callback(f"Pivote cero en F{i + 1}. Intercambiando F{i + 1} con F{k + 1}.", "step")
                    log_callback(format_matrix(A), "matrix")
                    pivot_found = True
                    break

            if not pivot_found:
                raise ValueError(
                    f"Error: Pivote cero en la columna {i + 1}. El sistema podría no tener solución única.")

        # --- Acumular el determinante ---
        determinant *= A[i, i]

        # --- Eliminación ---
        for j in range(i + 1, n):
            # Calculamos el factor
            factor = A[j, i] / A[i, i]

            # Operación de fila
            A[j, i:] = A[j, i:] - factor * A[i, i:]

            log_callback(f"\nPaso: F{j + 1} = F{j + 1} - ({factor:.4f}) * F{i + 1}", "step")
            log_callback(format_matrix(A), "matrix")

            # yield para pausar la ejecución y permitir que la UI se actualice
            yield f"Eliminación en F{j + 1}"

    # --- Condicionamiento ---
    final_det = determinant * (-1) ** swap_count  # Ajustar por intercambios

    log_callback("\n--- Análisis de Estabilidad del Sistema ---", "step")
    log_callback(f"Determinante de la matriz A: {final_det:.4e}", "matrix")

    # Ombral pequeño (epsilon) para comparar con cero
    if np.abs(final_det) < 1e-10:
        log_callback("ADVERTENCIA: El determinante es muy cercano a cero.", "error")
        log_callback("El sistema está mal condicionado o es singular (podría no tener solución única).", "error")
        log_callback("Los resultados pueden ser numéricamente inestables.\n", "error")
    else:
        log_callback("Sistema estable (determinante no es cero).\n", "step")

    log_callback("\nMatriz Triangulada (Fase de Eliminación Completa):", "step")
    log_callback(format_matrix(A), "matrix")

    # Sustitución Hacia Atrás
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        # Suma de A[i, j] * x[j] para j > i
        sum_ax = np.dot(A[i, i + 1:n], x[i + 1:n])

        # Despejar x[i]
        x[i] = (A[i, n] - sum_ax) / A[i, i]
        log_callback(f"Sustitución hacia atrás: x{i + 1} = {x[i]:.4f}", "step")
        yield f"Calculando x{i + 1}"

    # Devolver la solución final
    yield x
