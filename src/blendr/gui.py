"""tkinter GUI for blendr.

A thin layer over :mod:`blendr.core`, :mod:`blendr.formatting`, and
:mod:`blendr.storage`. It holds an in-memory list of fills and recomputes the
position summary on every change.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_tcl_tk_library_paths() -> None:
    """Point Tcl/Tk at the interpreter's bundled library directories.

    uv's standalone Python ships Tcl/Tk under ``sys.base_prefix``, but a
    virtual environment does not inherit that path, so creating a ``Tk()`` root
    fails to find ``init.tcl``. When the env vars are unset, locate the bundled
    library dirs and set them, so ``uv run blendr`` works out of the box. This
    is a no-op when Tcl/Tk is already configured.
    """
    lib = Path(sys.base_prefix) / "lib"
    for env_var, pattern, marker in (
        ("TCL_LIBRARY", "tcl8.*", "init.tcl"),
        ("TK_LIBRARY", "tk8.*", "tk.tcl"),
    ):
        if os.environ.get(env_var):
            continue
        for candidate in sorted(lib.glob(pattern), reverse=True):
            if (candidate / marker).is_file():
                os.environ[env_var] = str(candidate)
                break


_ensure_tcl_tk_library_paths()

import tkinter as tk  # noqa: E402
import tkinter.font as tkfont  # noqa: E402
from tkinter import filedialog, messagebox, ttk  # noqa: E402

from blendr import storage  # noqa: E402
from blendr.core import (  # noqa: E402
    Fill,
    average_entry_price,
    parse_decimal,
    total_cost,
    total_quantity,
)
from blendr.formatting import format_money, format_qty  # noqa: E402

_FILE_TYPES = [("blendr position", "*.json"), ("All files", "*.*")]


class BlendrApp:
    """The blendr main window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.fills: list[Fill] = []
        self.current_path: Path | None = None

        self._bold_font = tkfont.nametofont("TkDefaultFont").copy()
        self._bold_font.configure(weight="bold")

        self._build_menu()
        self._build_widgets()
        self._refresh()

        # Size the window to fit its contents snugly (the input row sets the
        # minimum width) so there's no wasted space and no clipped controls.
        root.update_idletasks()
        min_width = root.winfo_reqwidth()
        root.minsize(min_width, 300)
        root.geometry(f"{min_width}x420")

    # --- layout ---------------------------------------------------------

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open…", command=self._on_open, accelerator="Cmd+O")
        file_menu.add_command(label="Save", command=self._on_save, accelerator="Cmd+S")
        file_menu.add_command(label="Save As…", command=self._on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        for seq in ("<Command-o>", "<Control-o>"):
            self.root.bind(seq, lambda _e: self._on_open())
        for seq in ("<Command-s>", "<Control-s>"):
            self.root.bind(seq, lambda _e: self._on_save())

    def _build_widgets(self) -> None:
        # Input row.
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=6, pady=(6, 1))
        ttk.Label(input_frame, text="Price").grid(row=0, column=0, sticky="w")
        self.price_entry = ttk.Entry(input_frame, width=10)
        self.price_entry.grid(row=0, column=1, padx=(3, 8))
        ttk.Label(input_frame, text="Qty").grid(row=0, column=2, sticky="w")
        self.qty_entry = ttk.Entry(input_frame, width=10)
        self.qty_entry.grid(row=0, column=3, padx=(3, 8))
        ttk.Button(input_frame, text="Add", command=self._on_add).grid(row=0, column=4)
        for entry in (self.price_entry, self.qty_entry):
            entry.bind("<Return>", lambda _e: self._on_add())

        # Inline validation message.
        self.error_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.error_var, foreground="red").pack(
            fill="x", padx=6
        )

        # Fills table.
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=6, pady=2)
        columns = ("price", "quantity", "cost")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        for key, heading in zip(columns, ("Price", "Quantity", "Cost")):
            self.tree.heading(key, text=heading)
            self.tree.column(key, anchor="e", width=104, minwidth=60, stretch=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Row actions.
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=6, pady=2)
        ttk.Button(button_frame, text="Remove selected", command=self._on_remove).pack(
            side="left"
        )
        ttk.Button(button_frame, text="Clear all", command=self._on_clear).pack(
            side="left", padx=6
        )
        self.topmost_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            button_frame,
            text="Stay on top",
            variable=self.topmost_var,
            command=self._on_toggle_topmost,
        ).pack(side="right")

        # Results panel.
        results = ttk.LabelFrame(self.root, text="Position")
        results.pack(fill="x", padx=6, pady=(2, 6))
        results.columnconfigure(1, weight=1)
        self.avg_var = tk.StringVar()
        self.total_qty_var = tk.StringVar()
        self.total_cost_var = tk.StringVar()
        self._result_row(results, 0, "Average entry:", self.avg_var)
        self._result_row(results, 1, "Total quantity:", self.total_qty_var)
        self._result_row(results, 2, "Total cost:", self.total_cost_var)

    def _result_row(self, parent: ttk.LabelFrame, row: int, label: str, var: tk.StringVar) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=1)
        ttk.Label(parent, textvariable=var, font=self._bold_font, anchor="e").grid(
            row=row, column=1, sticky="e", padx=6, pady=1
        )

    # --- actions --------------------------------------------------------

    def _on_add(self) -> None:
        try:
            price = parse_decimal(self.price_entry.get())
        except ValueError as exc:
            self._show_error(f"Price: {exc}", self.price_entry)
            return
        try:
            quantity = parse_decimal(self.qty_entry.get())
        except ValueError as exc:
            self._show_error(f"Quantity: {exc}", self.qty_entry)
            return

        self.fills.append(Fill(price, quantity))
        self.error_var.set("")
        self.price_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.price_entry.focus_set()
        self._refresh()

    def _on_remove(self) -> None:
        selection = self.tree.selection()
        if not selection:
            self.error_var.set("Select a row to remove.")
            return
        del self.fills[int(selection[0])]
        self.error_var.set("")
        self._refresh()

    def _on_clear(self) -> None:
        if not self.fills:
            return
        if not messagebox.askyesno("Clear all", "Remove all fills?"):
            return
        self.fills.clear()
        self.error_var.set("")
        self._refresh()

    def _on_toggle_topmost(self) -> None:
        self.root.attributes("-topmost", self.topmost_var.get())

    def _on_open(self) -> None:
        path = filedialog.askopenfilename(title="Open position", filetypes=_FILE_TYPES)
        if not path:
            return
        try:
            fills = storage.load(path)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not open file", str(exc))
            return
        self.fills = fills
        self.current_path = Path(path)
        self.error_var.set("")
        self._refresh()

    def _on_save(self) -> None:
        if self.current_path is None:
            self._on_save_as()
            return
        self._write(self.current_path)

    def _on_save_as(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save position", defaultextension=".json", filetypes=_FILE_TYPES
        )
        if not path:
            return
        self.current_path = Path(path)
        self._write(self.current_path)

    def _write(self, path: Path) -> None:
        try:
            storage.save(self.fills, path)
        except OSError as exc:
            messagebox.showerror("Could not save file", str(exc))
            return
        self._refresh()

    # --- rendering ------------------------------------------------------

    def _show_error(self, message: str, focus: ttk.Entry) -> None:
        self.error_var.set(message)
        focus.focus_set()

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for index, fill in enumerate(self.fills):
            cost = fill.price * fill.quantity
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    format_money(fill.price),
                    format_qty(fill.quantity),
                    format_money(cost),
                ),
            )
        self.avg_var.set(format_money(average_entry_price(self.fills)))
        self.total_qty_var.set(format_qty(total_quantity(self.fills)))
        self.total_cost_var.set(format_money(total_cost(self.fills)))
        name = self.current_path.name if self.current_path else "Untitled"
        self.root.title(f"blendr — {name}")


def main() -> None:
    """Launch the blendr GUI."""
    root = tk.Tk()
    BlendrApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
