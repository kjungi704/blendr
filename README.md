# blendr

A small desktop GUI that calculates the **weighted-average entry price** of a
trading position from a list of buy fills.

Add each buy as a `(price, quantity)` row; blendr shows the average entry
price, total quantity, and total cost, updating live as you add or remove
rows. You can save a position to a JSON file and load it again later.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python, the virtualenv, and
  dependencies). The pinned Python — 3.11.5, from uv's standalone builds —
  bundles tkinter, so no system Tk install is needed.

## Run

```sh
uv run blendr
```

## Test

```sh
uv run pytest
```

## How the average is calculated

The average entry price is quantity-weighted:

```
average = sum(price_i * quantity_i) / sum(quantity_i)
```

So 0.5 @ 30,000 and 0.5 @ 25,000 gives an average of 27,500 — not a plain
mid-price, because each fill is weighted by its size.

## Project layout

```
src/blendr/
├── core.py         # Fill model + weighted-average math (pure)
├── formatting.py   # number display helpers (pure)
├── storage.py      # save/load fills <-> JSON (pure)
└── gui.py          # tkinter app + main() entry point
tests/              # pytest suite for the pure modules
docs/plans/         # design document
```

The math, formatting, and storage are pure modules with no GUI imports, so
they are unit-tested directly; the tkinter layer is kept thin.
