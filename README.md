<div align="center">

<img src="assets/suzanne.svg" alt="Suzanne, the blendr mascot" width="172" />

# `blendr`

**a dead-simple desktop calculator for your average entry price** <br>
*because doing quantity-weighted averages in your head is how you end up underwater*

`────────────  ⌐■_■  ────────────`

![python](https://img.shields.io/badge/python-3.11.5-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/built%20with-uv-DE5FE9)
![gui](https://img.shields.io/badge/gui-tkinter-FF6F61)
![tests](https://img.shields.io/badge/tests-34%20passing-3fb950)
![runtime deps](https://img.shields.io/badge/runtime%20deps-0-black)
![vibes](https://img.shields.io/badge/vibes-immaculate-ff69b4)

</div>

---

## what even is this

You buy a bag in pieces — a little here, a little there, averaging down like a champ (or coping, hard to say). `blendr` takes every fill you punch in and spits out the **one number that matters**: your true, quantity-weighted entry.

No spreadsheets. No "let me just open the calculator app." No floating-point lies — it's all `Decimal` under the hood, exact down to the last digit.

## the lore (a.k.a. why a monkey)

`blendr` ≈ Blender. Blender's mascot is **Suzanne**, a low-poly monkey head that has haunted 3D nerds since 2002. She has no notes. She is just *here*. Now she's here too, judging your unrealized PnL. 🐵

## quickstart

```sh
uv run blendr      # open the window
uv run pytest      # run the 34 tests (they pass — checked twice)
```

That's the whole setup. `uv` handles Python 3.11.5, the venv, and tkinter — no `brew install` rituals, no system Tk.

## the one formula

A quantity-weighted average, not a naive mid:

```
avg entry = Σ(priceᵢ × qtyᵢ) / Σ(qtyᵢ)
```

> 0.5 @ 30,000 and 0.5 @ 25,000 → **27,500**, because each fill pulls its own weight.

## how to drive it

| do this | get that |
|---|---|
| type a **Price** + **Qty**, hit **Add** (or `Enter`) | a new row in the table |
| select a row → **Remove selected** | one fewer regret |
| **Clear all** | a clean slate (it asks first) |
| **Stay on top** ☑ | window floats above everything else |
| **File → Save As…** / `⌘S` | dumps your fills to a `.json` |
| **File → Open…** / `⌘O` | loads them back |

> heads-up: the menu lives in the macOS menu bar at the top of the screen. Text you've typed but haven't **Add**-ed yet isn't part of your data.

## under the hood

```
src/blendr/
├── core.py        # the math: weighted avg, totals, Decimal parsing
├── formatting.py  # commas, trimmed decimals, the lonely em-dash
├── storage.py     # fills ⇄ JSON, validated on the way in
└── gui.py         # tkinter, kept deliberately dumb
```

The math, formatting, and storage layers are pure and tested to death; the GUI is a thin shell on top. Boring on purpose.

---

<div align="center">
<sub>built with uv, tkinter, and an unreasonable amount of <code>Decimal</code> · Suzanne sees your average entry</sub>
</div>
