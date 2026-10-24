"""How the model works, what the data is, and what is not claimed."""

import app_shell as shell
import ui_components as ui

shell.page_header("Method & data", "The dispatch cost formula, the three quantities that must not be confused, "
                  "where the data comes from, and the limits of this work.", scenario_picker=True, eyebrow="About")
scen = shell.current_scenario()
shell.set_active(scen)
ui.render_methodology(scenario=scen)
