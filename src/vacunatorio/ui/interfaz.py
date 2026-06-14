import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.vacunatorio.config.constantes import (
    COEFICIENTE_RK_DERECHO,
    COEFICIENTE_RK_IZQUIERDO,
)
from src.vacunatorio.config.parametros import Parametros, validar_parametros
from src.vacunatorio.simulacion.motor import Simulacion
from src.vacunatorio.utils.utilidades import formatear_numero


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulacion Vacunatorio")
        self.geometry("1500x820")
        self.minsize(1200, 700)
        self.resultado = None
        self.filas_vector_actuales = []
        self.variables = {}
        self.crear_interfaz()

    def crear_interfaz(self):
        contenedor = ttk.Frame(self, padding=10)
        contenedor.pack(fill="both", expand=True)

        panel_parametros = ttk.Frame(contenedor)
        panel_parametros.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(panel_parametros, text="Parametros", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.crear_campos(panel_parametros)

        ttk.Button(panel_parametros, text="Simular", command=self.ejecutar_simulacion).pack(fill="x", pady=(12, 4))
        ttk.Button(panel_parametros, text="Exportar vector CSV", command=self.exportar_csv).pack(fill="x")

        notas = (
            "Ecuacion RK fija del enunciado:\n"
            f"{COEFICIENTE_RK_IZQUIERDO} * R = dR/dt + {COEFICIENTE_RK_DERECHO} * R\n\n"
            "La interrupcion es periodica y pausa al enfermero."
        )
        ttk.Label(panel_parametros, text=notas, justify="left").pack(anchor="w", pady=12)

        panel_resultados = ttk.Notebook(contenedor)
        panel_resultados.pack(side="right", fill="both", expand=True)

        self.tab_vector = ttk.Frame(panel_resultados)
        self.tab_estadisticas = ttk.Frame(panel_resultados)
        self.tab_rk = ttk.Frame(panel_resultados)
        panel_resultados.add(self.tab_vector, text="Vector de estado")
        panel_resultados.add(self.tab_estadisticas, text="Estadisticas")
        panel_resultados.add(self.tab_rk, text="Runge-Kutta")

        self.crear_panel_vector()
        self.tabla_estadisticas = self.crear_tabla(self.tab_estadisticas)
        self.tabla_rk = self.crear_tabla(self.tab_rk)

    def crear_panel_vector(self):
        panel_superior = ttk.Frame(self.tab_vector)
        panel_superior.pack(fill="both", expand=True)

        ttk.Label(panel_superior, text="Vector de estado").pack(anchor="w")
        self.tabla_vector = self.crear_tabla(panel_superior)
        self.tabla_vector.bind("<<TreeviewSelect>>", self.mostrar_detalle_pacientes)

        panel_detalle = ttk.LabelFrame(self.tab_vector, text="Detalle de pacientes de la fila seleccionada", padding=6)
        panel_detalle.pack(fill="both", expand=True, pady=(8, 0))

        self.texto_detalle = tk.StringVar(value="Seleccione una fila para ver los pacientes presentes.")
        ttk.Label(panel_detalle, textvariable=self.texto_detalle).pack(anchor="center", pady=(0, 4))
        self.tabla_detalle_pacientes = self.crear_tabla(panel_detalle, alto=8)

    def crear_campos(self, padre):
        grupos = [
            ("Simulacion", [
                ("tiempo_simulacion", "Tiempo X simulacion (seg)", 28800),
                ("max_iteraciones", "Max iteraciones", 100000),
                ("mostrar_desde", "Mostrar desde iteracion j", 0),
                ("mostrar_cantidad", "Mostrar cantidad i", 200),
                ("semilla", "Semilla", 12345),
            ]),
            ("Llegadas y vacunas", [
                ("media_llegada_covid", "Media llegada COVID (seg)", 225),
                ("media_llegada_gripe", "Media llegada gripe (seg)", 300),
                ("dosis_caja_covid", "Dosis caja COVID", 5),
                ("dosis_caja_gripe", "Dosis caja gripe", 10),
                ("tiempo_por_paciente", "Segundos por paciente", 22),
            ]),
            ("Interrupcion", [
                ("intervalo_interrupcion", "Cada cuantos seg ocurre", 3600),
                ("duracion_interrupcion", "Duracion interrupcion (seg)", 300),
            ]),
            ("Runge-Kutta", [
                ("rk_r_inicial", "R inicial", 1),
                ("rk_t_inicial", "t inicial", 0),
                ("rk_t_final", "t final RK", 0.2),
                ("rk_paso", "Paso h", 0.01),
            ]),
        ]

        for titulo, campos in grupos:
            marco = ttk.LabelFrame(padre, text=titulo, padding=8)
            marco.pack(fill="x", pady=4)
            for atributo, etiqueta, valor in campos:
                fila = ttk.Frame(marco)
                fila.pack(fill="x", pady=2)
                ttk.Label(fila, text=etiqueta, width=28).pack(side="left")
                variable = tk.StringVar(value=str(valor))
                self.variables[atributo] = variable
                ttk.Entry(fila, textvariable=variable, width=12).pack(side="right")

    def leer_parametros(self):
        p = Parametros()
        enteros = {
            "max_iteraciones",
            "mostrar_desde",
            "mostrar_cantidad",
            "semilla",
            "dosis_caja_covid",
            "dosis_caja_gripe",
        }
        for atributo, variable in self.variables.items():
            texto = variable.get().replace(",", ".")
            valor = int(float(texto)) if atributo in enteros else float(texto)
            setattr(p, atributo, valor)
        validar_parametros(p)
        return p

    def ejecutar_simulacion(self):
        try:
            parametros = self.leer_parametros()
            simulacion = Simulacion(parametros)
            self.resultado = simulacion.simular()
            self.cargar_vector(self.resultado["filas"])
            self.cargar_estadisticas(self.resultado["estadisticas"])
            self.cargar_rk(self.resultado["rk"])
        except Exception as error:
            messagebox.showerror("No se pudo simular", str(error))

    def crear_tabla(self, padre, alto=15):
        marco = ttk.Frame(padre)
        marco.pack(fill="both", expand=True)
        tabla = ttk.Treeview(marco, show="headings", height=alto)
        scroll_y = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        scroll_x = ttk.Scrollbar(marco, orient="horizontal", command=tabla.xview)
        tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)
        return tabla

    def configurar_columnas(self, tabla, columnas):
        tabla.delete(*tabla.get_children())
        tabla["columns"] = columnas
        for columna in columnas:
            ancho = self.ancho_columna(columna)
            tabla.heading(columna, text=columna)
            tabla.column(columna, width=ancho, minwidth=ancho, anchor="center", stretch=False)

    def ancho_columna(self, columna):
        anchos_especiales = {
            "Iteracion": 78,
            "Reloj (seg)": 96,
            "Evento": 150,
            "Estado enfermero": 142,
            "Pacientes presentes": 142,
            "RND grupo llegada": 132,
            "Tam grupo llegada": 132,
            "Dosis descartadas evento": 170,
            "Estadistica": 250,
            "Valor": 140,
            "Inicio vacunacion": 128,
        }
        if columna in anchos_especiales:
            return anchos_especiales[columna]
        return max(72, len(columna) * 8 + 18)

    def cargar_vector(self, filas):
        if not filas:
            self.filas_vector_actuales = []
            self.configurar_columnas(self.tabla_vector, ["Estado"])
            self.tabla_vector.insert("", "end", values=["No hay filas para el rango solicitado"])
            self.limpiar_detalle_pacientes()
            return
        columnas = self.columnas_visibles(filas)
        self.configurar_columnas(self.tabla_vector, columnas)
        self.filas_vector_actuales = filas
        for indice, fila in enumerate(filas):
            valores = [formatear_numero(fila[columna]) for columna in columnas]
            self.tabla_vector.insert("", "end", iid=str(indice), values=valores)
        self.limpiar_detalle_pacientes()

    def columnas_visibles(self, filas):
        columnas = list(filas[0].keys())
        return [
            columna
            for columna in columnas
            if not columna.startswith("_") and columna != "Detalle pacientes"
        ]

    def limpiar_detalle_pacientes(self):
        columnas = ["ID", "Vacuna", "Estado", "Llegada (seg)", "Grupo", "Inicio vacunacion"]
        self.configurar_columnas(self.tabla_detalle_pacientes, columnas)
        self.texto_detalle.set("Seleccione una fila para ver los pacientes presentes.")

    def mostrar_detalle_pacientes(self, _evento=None):
        seleccion = self.tabla_vector.selection()
        self.limpiar_detalle_pacientes()
        if not seleccion:
            return

        indice = int(seleccion[0])
        objetos = self.filas_vector_actuales[indice].get("_objetos", [])
        self.texto_detalle.set(f"Pacientes presentes: {len(objetos)}")
        columnas = self.tabla_detalle_pacientes["columns"]
        for objeto in objetos:
            valores = [formatear_numero(objeto[columna]) for columna in columnas]
            self.tabla_detalle_pacientes.insert("", "end", values=valores)

    def cargar_estadisticas(self, estadisticas):
        columnas = ["Estadistica", "Valor"]
        self.configurar_columnas(self.tabla_estadisticas, columnas)
        for nombre, valor in estadisticas:
            self.tabla_estadisticas.insert("", "end", values=[nombre, formatear_numero(valor)])

    def cargar_rk(self, filas):
        if not filas:
            return
        columnas = list(filas[0].keys())
        self.configurar_columnas(self.tabla_rk, columnas)
        for fila in filas:
            self.tabla_rk.insert("", "end", values=[formatear_numero(fila[c]) for c in columnas])

    def exportar_csv(self):
        if not self.resultado:
            messagebox.showinfo("Exportar", "Primero ejecuta una simulacion.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Guardar vector de estado",
        )
        if not ruta:
            return

        filas = self.resultado["filas"]
        columnas = self.columnas_visibles(filas)
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=columnas, extrasaction="ignore")
            escritor.writeheader()
            escritor.writerows(filas)
        messagebox.showinfo("Exportar", "Vector exportado correctamente.")
