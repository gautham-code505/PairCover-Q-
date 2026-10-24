# PairCover-Q design system

The app has one rule for design: **a viewer should be able to tell what is happening from the colours and the one-line status alone.** Everything below serves that rule. Change values here and in the files named; nothing else needs to change.

## 1. Colour meanings

Each colour means one thing, everywhere: the console, the map, badges and charts.

| Meaning | Token | Light | Dark | Used for |
|---|---|---|---|---|
| Emergency call | `--red` | `#C62828` | `#FF6B6B` | Call markers on the map, priority chips, unserved calls, errors |
| Ambulance dispatched / main action | `--blue` | `#0B63C4` | `#5AA9FF` | Dispatched routes, moving unit markers, primary buttons, section labels |
| Held in reserve / backup kept / valid | `--teal` (green) | `#16803C` | `#3DDC97` | "held" units, "backup kept", feasible badges, the optimum in charts |
| Coverage at risk | `--amber` | `#A15C00` | `#F5B946` | Backup pair shading, coverage penalty, warnings |
| Quantum | `--violet` | `#6D4AD6` | `#B69CFF` | QAOA results, optimiser trace, quantum badges |

`--teal` keeps its old name so existing code works, but it is green.

**Neutrals:** background `--bg`, cards `--surface`, raised areas `--surface2`, lines `--border` and `--divider`, and text `--text` and `--muted`. Light values are near-white with dark text; dark values are a blue-black with light text.

## 2. Where to change things

| To change | Edit |
|---|---|
| Any colour in custom parts (cards, map, steps, status line) | The `:root` block at the top of `_CSS` in `app/ui_components.py`. Each token is `light-dark(<light>, <dark>)`. |
| Colours of Streamlit's own widgets (buttons, inputs, tables) | `.streamlit/config.toml`, sections `[theme.light]` and `[theme.dark]` |
| Chart colours (Plotly) | `_PALETTES` in `app/ui_components.py`; keep it in step with the `:root` tokens |
| Font | `font` and `codeFont` in `.streamlit/config.toml` (IBM Plex Sans and IBM Plex Mono) |
| Status-line wording | `status_sentence()` in `app/ui_helpers.py` |
| Step names | `workflow_steps()` in `app/ui_helpers.py` |
| Method names shown to users | `_METHOD_DISPLAY` in `app/ui_helpers.py` |

## 3. How light/dark works

- `.streamlit/config.toml` defines both `[theme.light]` and `[theme.dark]`. Without a choice, the app follows the viewer's device setting.
- The **☀ / ☾** switch in every page header reloads the app with Streamlit's `embed_options=light_theme` or `dark_theme`. Streamlit only applies a theme on page load, so switching starts a new session and clears runs. Switch before a demo, not during one.
- Streamlit marks the active mode on the page, and every custom colour is written as `light-dark(light, dark)`, so the CSS follows automatically. Python code that needs a colour (Plotly) calls `theme_mode()`.

## 4. App structure

The app is a multi-page Streamlit app with a top navigation bar (`app/main.py`, pages in `app/app_pages/`):

| Menu | Page | URL | Purpose |
|---|---|---|---|
| Home | `home.py` | `/` | Headline, the animated "decision film" (the coverage demo's two real decisions), how it works, evidence tiles, honesty note |
| Try it | `console.py` | `/console` | The dispatch console on the fixed scenarios |
| Try it | `your_emergency.py` | `/your_emergency` | Build your own emergency on the synthetic city |
| Quantum | `quantum_lab.py` | `/quantum_lab` | QAOA settings, optimiser trace, measured samples |
| Quantum | `results.py` | `/results` | Every valid plan ranked; runs compared |
| About | `evidence.py` | `/evidence` | Round 2 studies with their own charts |
| About | `method.py` | `/method` | Formula, quantities, data provenance, limits |

Every page starts with the same header from `app_shell.page_header()`: title and one-line purpose on the left; scenario picker (where it applies), the ☀/☾ theme switch and a ⚙ settings menu on the right. There is no sidebar. Streamlit's developer toolbar is hidden (`[client] toolbarMode = "minimal"`).

**Type:** Barlow Semi Condensed for titles and display numbers (`--display`), IBM Plex Sans for body text, IBM Plex Mono for code.

**Logo:** `app/assets/logo.svg`. A medical cross above two linked dots: the backup pair that PairCover-Q protects.

## 5. Console layout, top to bottom

1. **Page header**, as above.
2. **Stats bar:** open calls, available units, backup pairs and the latest cost.
3. **Step bar:** Calls arrive, Choose a method, Run it, Compare & see why. Finished steps show ✓ and the current step is outlined in blue.
4. **Colour key:** the five meanings from section 1.
5. **Status line:** one plain sentence about what is on screen, built only from the shown result. Its left edge takes the result's colour: green for backup kept, amber for coverage lost, violet for QAOA.
6. **Three columns:** calls and units, the zone map, and the method picker with the result card. These come first so they fit on a laptop screen.
7. **Result summary:** cost tiles and the trade-off sentence (after a run).
8. **"Why it changed":** shown after two methods, then the run ledger.

## 6. Rules that must not change

- Nothing is shown as a result unless it was computed in this session or enumerated from the scenario.
- Colour is never the only signal. Every state also has a word (held, unserved, feasible) or an icon.
- The map is a synthetic grid where distance equals minutes. It is never presented as a real map.
- Animation can be paused, and it stops for users who ask for reduced motion.
