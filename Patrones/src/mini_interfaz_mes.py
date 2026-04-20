"""
Mini interfaz de escritorio para el proyecto MES funcional.

Ejecucion:
python mini_interfaz_mes.py
"""

from __future__ import annotations

import json
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from mes_functional_app import OrderExecutionRequest, build_default_mes_project


class MESMiniUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MES Functional UI - Patrones")
        self.geometry("1220x760")
        self.minsize(1100, 680)

        self.app = build_default_mes_project()
        self._build_theme()
        self._build_layout()
        self._load_example_cnc()

    def _build_theme(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Card.TFrame", background="#f5f7fb")
        style.configure("Header.TLabel", font=("Segoe UI", 15, "bold"), background="#f5f7fb")
        style.configure("Hint.TLabel", font=("Segoe UI", 10), foreground="#3e4a5f", background="#f5f7fb")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        root = ttk.Frame(self, style="Card.TFrame", padding=14)
        root.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(root, text="Sistema MES - Ejecucion Funcional", style="Header.TLabel")
        title.pack(anchor="w")
        subtitle = ttk.Label(
            root,
            text="Ingresa datos, ejecuta una orden y revisa la salida por patron.",
            style="Hint.TLabel",
        )
        subtitle.pack(anchor="w", pady=(2, 10))

        top = ttk.LabelFrame(root, text="Entradas de orden", padding=10)
        top.pack(fill=tk.X)

        self.template_var = tk.StringVar()
        self.order_id_var = tk.StringVar()
        self.units_var = tk.StringVar()
        self.shift_var = tk.StringVar()
        self.protocol_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Listo para ejecutar.")

        self._build_input_row(top)

        actions = ttk.Frame(top)
        actions.grid(row=2, column=0, columnspan=8, sticky="ew", pady=(10, 0))
        actions.columnconfigure(7, weight=1)

        ttk.Button(actions, text="Ejemplo CNC", command=self._load_example_cnc).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Ejemplo Robot", command=self._load_example_robot).grid(row=0, column=1, padx=4)
        ttk.Button(actions, text="Reiniciar contexto", command=self._reset_context).grid(row=0, column=2, padx=4)
        ttk.Button(actions, text="Ejecutar orden", style="Primary.TButton", command=self._execute).grid(
            row=0, column=3, padx=8
        )
        ttk.Label(actions, textvariable=self.status_var, style="Hint.TLabel").grid(
            row=0, column=7, sticky="e", padx=(12, 0)
        )

        body = ttk.Frame(root)
        body.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.tabs = ttk.Notebook(body)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.summary_text = ScrolledText(self.tabs, wrap=tk.WORD, font=("Consolas", 10))
        self.summary_text.configure(state=tk.DISABLED)
        self.tabs.add(self.summary_text, text="Resumen")

        self.log_tree = ttk.Treeview(
            self.tabs,
            columns=("step", "pattern", "module", "evidence"),
            show="headings",
            height=18,
        )
        for col, width in (
            ("step", 290),
            ("pattern", 150),
            ("module", 230),
            ("evidence", 470),
        ):
            self.log_tree.heading(col, text=col.capitalize())
            self.log_tree.column(col, width=width, anchor="w")
        self.tabs.add(self.log_tree, text="Bitacora de patrones")

        self.report_text = ScrolledText(self.tabs, wrap=tk.WORD, font=("Consolas", 10))
        self.report_text.configure(state=tk.DISABLED)
        self.tabs.add(self.report_text, text="Reporte final")

        self.map_tree = ttk.Treeview(
            self.tabs,
            columns=("pattern", "module", "classes", "usage"),
            show="headings",
            height=18,
        )
        for col, width in (
            ("pattern", 130),
            ("module", 220),
            ("classes", 330),
            ("usage", 430),
        ):
            self.map_tree.heading(col, text=col.capitalize())
            self.map_tree.column(col, width=width, anchor="w")
        self.tabs.add(self.map_tree, text="Mapa patron-codigo")

    def _build_input_row(self, parent: ttk.LabelFrame) -> None:
        ttk.Label(parent, text="Template").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        template = ttk.Combobox(
            parent,
            textvariable=self.template_var,
            values=["cnc_standard", "robot_packaging"],
            state="readonly",
            width=20,
        )
        template.grid(row=1, column=0, sticky="ew", padx=4, pady=4)

        ttk.Label(parent, text="Order ID").grid(row=0, column=1, sticky="w", padx=4, pady=4)
        ttk.Entry(parent, textvariable=self.order_id_var, width=22).grid(
            row=1, column=1, sticky="ew", padx=4, pady=4
        )

        ttk.Label(parent, text="Planned units").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(parent, textvariable=self.units_var, width=14).grid(
            row=1, column=2, sticky="ew", padx=4, pady=4
        )

        ttk.Label(parent, text="Shift").grid(row=0, column=3, sticky="w", padx=4, pady=4)
        shift = ttk.Combobox(
            parent,
            textvariable=self.shift_var,
            values=["DAY", "NIGHT"],
            state="readonly",
            width=14,
        )
        shift.grid(row=1, column=3, sticky="ew", padx=4, pady=4)

        ttk.Label(parent, text="Protocol").grid(row=0, column=4, sticky="w", padx=4, pady=4)
        protocol = ttk.Combobox(
            parent,
            textvariable=self.protocol_var,
            values=["opcua", "modbus"],
            state="readonly",
            width=14,
        )
        protocol.grid(row=1, column=4, sticky="ew", padx=4, pady=4)

        for idx in range(5):
            parent.columnconfigure(idx, weight=1)

    def _load_example_cnc(self) -> None:
        now = datetime.now().strftime("%m%d%H%M")
        self.template_var.set("cnc_standard")
        self.order_id_var.set(f"OP-2026-{now}")
        self.units_var.set("600")
        self.shift_var.set("DAY")
        self.protocol_var.set("opcua")
        self.status_var.set("Ejemplo CNC cargado.")

    def _load_example_robot(self) -> None:
        now = datetime.now().strftime("%m%d%H%M")
        self.template_var.set("robot_packaging")
        self.order_id_var.set(f"OP-2026-{now}")
        self.units_var.set("420")
        self.shift_var.set("NIGHT")
        self.protocol_var.set("modbus")
        self.status_var.set("Ejemplo Robot cargado.")

    def _reset_context(self) -> None:
        self.app = build_default_mes_project()
        self._clear_outputs()
        self.status_var.set("Contexto reiniciado.")

    def _clear_outputs(self) -> None:
        self._set_text(self.summary_text, "")
        self._set_text(self.report_text, "")
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        for item in self.map_tree.get_children():
            self.map_tree.delete(item)

    def _execute(self) -> None:
        try:
            units = int(self.units_var.get().strip())
            if units <= 0:
                raise ValueError("Planned units debe ser mayor que cero.")

            request = OrderExecutionRequest(
                template_key=self.template_var.get().strip(),
                order_id=self.order_id_var.get().strip(),
                planned_units=units,
                shift=self.shift_var.get().strip(),
                protocol=self.protocol_var.get().strip(),
            )
            self.status_var.set("Procesando orden...")
            self.update_idletasks()

            result = self.app.execute_order(request)
            self._render_result(result)
            self.status_var.set("Orden ejecutada correctamente.")
            self.tabs.select(0)
        except Exception as exc:
            self.status_var.set("Error en ejecucion.")
            messagebox.showerror("MES UI", str(exc))

    def _render_result(self, result: dict) -> None:
        self._clear_outputs()

        summary_lines = []
        summary_lines.append(f"Status: {result.get('status')}")
        summary_lines.append(f"Order: {result.get('order_id', '-')}")
        if result.get("status") == "OK":
            summary_lines.append(f"Dispatch: {result.get('dispatch')}")
            summary_lines.append(f"Legacy sync: {result.get('legacy_sync')}")
            summary_lines.append(f"Plant capacity units: {result.get('plant_capacity_units')}")
            controller = result.get("controller_summary", {})
            summary_lines.append("")
            summary_lines.append("Controller summary:")
            for key, value in controller.items():
                summary_lines.append(f"  - {key}: {value}")
        else:
            summary_lines.append(f"Message: {result.get('message')}")
        self._set_text(self.summary_text, "\n".join(summary_lines))

        for idx, row in enumerate(result.get("execution_log", []), start=1):
            self.log_tree.insert(
                "",
                tk.END,
                values=(
                    f"{idx:02d}. {row.get('step', '')}",
                    row.get("pattern", ""),
                    row.get("module", ""),
                    row.get("evidence", ""),
                ),
            )

        self._set_text(
            self.report_text,
            json.dumps(result.get("final_report", {}), ensure_ascii=False, indent=2),
        )

        for item in result.get("implementation_map", []):
            self.map_tree.insert(
                "",
                tk.END,
                values=(
                    item.get("pattern", ""),
                    item.get("module", ""),
                    item.get("key_classes", ""),
                    item.get("usage_point", ""),
                ),
            )

    def _set_text(self, widget: ScrolledText, content: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
        widget.configure(state=tk.DISABLED)


def main() -> None:
    ui = MESMiniUI()
    ui.mainloop()


if __name__ == "__main__":
    main()
