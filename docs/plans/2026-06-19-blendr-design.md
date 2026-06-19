# blendr — Design

**Date:** 2026-06-19
**Status:** Approved

## Purpose

A simple desktop GUI app that calculates the **average entry price** of a
trading position from a list of buy fills.

## Scope (v1)

In scope:

- Add buy fills as rows of `(price, quantity)`.
- Show the weighted-average entry price, total quantity, and total cost,
  recomputed live on every change.
- Remove a selected row; clear all rows.
- Save and load the fills to/from a JSON file.
- Tidy number formatting (thousands separators, sensible decimals).

Out of scope (YAGNI):

- Trading fees.
- Long/short direction (the math is identical, so direction is ignored).
- Currency conversion or live market data.
- Profit/loss, liquidation, or position-sizing calculations.

## Stack

- **Python 3.11.5**, pinned via `.python-version` to a uv-managed standalone
  build (tkinter is bundled — no `brew install python-tk` needed).
- **uv** for project, environment, and runner.
- **tkinter** for the GUI (no third-party runtime dependencies).
- **pytest** for tests (dev dependency only).

## Architecture

The math is pure and lives apart from the GUI, so it is fully unit-testable
without a display. The GUI is a thin layer over the pure modules.

```
blendr/
├── pyproject.toml          # uv project; [project.scripts] blendr = "blendr.gui:main"
├── .python-version         # 3.11.5
├── README.md
├── src/blendr/
│   ├── __init__.py
│   ├── core.py             # Fill model + weighted-average math (pure)
│   ├── formatting.py       # number display helpers (pure)
│   ├── storage.py          # save/load fills <-> JSON (pure)
│   └── gui.py              # tkinter app + main() entry point
└── tests/
    ├── test_core.py
    ├── test_formatting.py
    └── test_storage.py
```

Run: `uv run blendr` launches the GUI. `uv run pytest` runs the tests.

## Core math (`core.py`)

Uses `Decimal` so price/quantity math is exact.

```python
@dataclass(frozen=True)
class Fill:
    price: Decimal      # > 0
    quantity: Decimal   # > 0

def total_quantity(fills) -> Decimal           # sum of quantities
def total_cost(fills) -> Decimal               # sum of price * quantity
def average_entry_price(fills) -> Decimal | None   # total_cost / total_quantity
```

- **Weighted average** = sum(price · qty) / sum(qty).
- **Empty / zero-quantity guard:** `average_entry_price` returns `None` (the UI
  shows `—`) and never divides by zero.
- **`parse_decimal(text)`** trims input, strips thousands separators, and
  rejects blank, non-numeric, or non-positive values by raising `ValueError`.

## Formatting (`formatting.py`)

- `format_money(d)` → `28,300.00` (2 decimals, thousands separators).
- `format_qty(d)` → up to 8 decimals with trailing zeros trimmed.
- `None` → `—`.

## Storage (`storage.py`)

- `save(fills, path)` writes JSON: `[{"price": "30000", "quantity": "0.5"}, …]`
  (Decimals serialized as strings to stay exact).
- `load(path)` parses and validates back into `Fill`s, raising on malformed
  files. The GUI surfaces save/load errors via a message box.

## GUI (`gui.py`)

Single resizable window, **520 × 620 px** initial, **460 × 520** minimum,
top-to-bottom:

1. **File menu** — Open…, Save…, Save As….
2. **Input row** — Price entry, Quantity entry, Add button (Enter key also
   adds). An inline red label shows validation errors.
3. **Fills table** — a scrollable `ttk.Treeview` with Price, Quantity, Cost
   columns; the table area stretches when the window grows.
4. **Buttons** — Remove selected, Clear all.
5. **Results panel** — Average entry, Total quantity, Total cost (bold),
   recomputed live on every add/remove/clear/open.

The app holds an in-memory `list[Fill]`; the table is a view of it.

## Error handling

- Invalid Add input → row not added, inline error shown.
- Save/load/parse failures → message box; in-memory state is left unchanged.

## Testing

`pytest` covers `core`, `formatting`, and `storage`, including:

- empty list, single fill, multi-fill weighted average;
- zero/negative/garbage input and comma handling;
- Decimal exactness;
- storage round-trip (save → load) and a malformed-file case.

The GUI has no unit tests — it is kept deliberately thin. The pure modules are
built test-first.
