"""Parameter control panel for the GUI."""

import tkinter as tk
from tkinter import ttk
from rendering.colors import PALETTES


class ControlPanel(ttk.Frame):
    """Side panel with pattern selection and parameter controls."""

    def __init__(self, parent, pattern_names, on_change):
        super().__init__(parent, padding=10)
        self.on_change = on_change
        self.param_widgets = {}
        self.param_vars = {}

        self._build_pattern_selector(pattern_names)
        self._build_palette_selector()
        self._build_render_options()
        self.param_frame = ttk.LabelFrame(self, text="Pattern Parameters", padding=5)
        self.param_frame.pack(fill="x", pady=(10, 0))

    def _build_pattern_selector(self, names):
        frame = ttk.LabelFrame(self, text="Pattern", padding=5)
        frame.pack(fill="x")

        self.pattern_var = tk.StringVar(value=names[0])
        combo = ttk.Combobox(frame, textvariable=self.pattern_var, values=names, state="readonly", width=20)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", lambda e: self.on_change("pattern"))

    def _build_palette_selector(self):
        frame = ttk.LabelFrame(self, text="Color Palette", padding=5)
        frame.pack(fill="x", pady=(10, 0))

        palette_names = list(PALETTES.keys())
        self.palette_var = tk.StringVar(value=palette_names[0])
        combo = ttk.Combobox(frame, textvariable=self.palette_var, values=palette_names, state="readonly", width=20)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", lambda e: self.on_change("palette"))

    def _build_render_options(self):
        frame = ttk.LabelFrame(self, text="Rendering", padding=5)
        frame.pack(fill="x", pady=(10, 0))

        # Line width
        ttk.Label(frame, text="Line Width").pack(anchor="w")
        self.line_width_var = tk.DoubleVar(value=1.0)
        lw_scale = ttk.Scale(frame, from_=0.5, to=5.0, variable=self.line_width_var,
                             orient="horizontal", command=lambda v: self.on_change("render"))
        lw_scale.pack(fill="x")

        # Glow effect
        self.glow_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Glow Effect", variable=self.glow_var,
                        command=lambda: self.on_change("render")).pack(anchor="w")

        # Gradient coloring
        self.gradient_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Gradient Colors", variable=self.gradient_var,
                        command=lambda: self.on_change("render")).pack(anchor="w")

        # Effects section
        fx_frame = ttk.LabelFrame(self, text="Effects", padding=5)
        fx_frame.pack(fill="x", pady=(10, 0))

        # Kaleidoscope
        ttk.Label(fx_frame, text="Kaleidoscope Folds (0=off)").pack(anchor="w")
        self.kaleidoscope_var = tk.IntVar(value=0)
        kal_sub = ttk.Frame(fx_frame)
        kal_sub.pack(fill="x")
        ttk.Scale(kal_sub, from_=0, to=12, variable=self.kaleidoscope_var,
                  orient="horizontal",
                  command=lambda v: self._kal_changed(v)).pack(side="left", fill="x", expand=True)
        self.kal_label = ttk.Label(kal_sub, text="0", width=3)
        self.kal_label.pack(side="right")

        # Gaussian glow
        self.gauss_glow_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(fx_frame, text="Gaussian Bloom", variable=self.gauss_glow_var,
                        command=lambda: self.on_change("render")).pack(anchor="w")

        # Vignette
        self.vignette_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(fx_frame, text="Vignette", variable=self.vignette_var,
                        command=lambda: self.on_change("render")).pack(anchor="w")

    def _kal_changed(self, value):
        int_val = int(float(value))
        self.kaleidoscope_var.set(int_val)
        self.kal_label.config(text=str(int_val))
        self.on_change("render")

    def build_params(self, param_defs):
        """Build parameter widgets from pattern's param definitions."""
        for w in self.param_frame.winfo_children():
            w.destroy()
        self.param_widgets.clear()
        self.param_vars.clear()

        for pdef in param_defs:
            name = pdef["name"]
            label = pdef.get("label", name)
            ptype = pdef["type"]
            default = pdef["default"]

            row = ttk.Frame(self.param_frame)
            row.pack(fill="x", pady=2)

            if ptype == "bool":
                var = tk.BooleanVar(value=default)
                ttk.Checkbutton(row, text=label, variable=var,
                                command=lambda: self.on_change("param")).pack(anchor="w")
            elif ptype == "int":
                ttk.Label(row, text=label).pack(anchor="w")
                var = tk.IntVar(value=default)
                sub = ttk.Frame(row)
                sub.pack(fill="x")
                scale = ttk.Scale(sub, from_=pdef["min"], to=pdef["max"],
                                  variable=var, orient="horizontal",
                                  command=lambda v, n=name: self._int_changed(n, v))
                scale.pack(side="left", fill="x", expand=True)
                val_label = ttk.Label(sub, text=str(default), width=5)
                val_label.pack(side="right")
                self.param_widgets[name + "_label"] = val_label
            elif ptype == "float":
                ttk.Label(row, text=label).pack(anchor="w")
                var = tk.DoubleVar(value=default)
                sub = ttk.Frame(row)
                sub.pack(fill="x")
                scale = ttk.Scale(sub, from_=pdef["min"], to=pdef["max"],
                                  variable=var, orient="horizontal",
                                  command=lambda v, n=name: self._float_changed(n, v))
                scale.pack(side="left", fill="x", expand=True)
                val_label = ttk.Label(sub, text=f"{default:.2f}", width=5)
                val_label.pack(side="right")
                self.param_widgets[name + "_label"] = val_label

            self.param_vars[name] = var

    def _int_changed(self, name, value):
        int_val = int(float(value))
        self.param_vars[name].set(int_val)
        label_key = name + "_label"
        if label_key in self.param_widgets:
            self.param_widgets[label_key].config(text=str(int_val))
        self.on_change("param")

    def _float_changed(self, name, value):
        label_key = name + "_label"
        if label_key in self.param_widgets:
            self.param_widgets[label_key].config(text=f"{float(value):.2f}")
        self.on_change("param")

    def get_params(self):
        """Get current parameter values as a dict."""
        return {name: var.get() for name, var in self.param_vars.items()}

    def get_render_settings(self):
        return {
            "palette": self.palette_var.get(),
            "line_width": self.line_width_var.get(),
            "glow": self.glow_var.get(),
            "gradient": self.gradient_var.get(),
            "kaleidoscope": self.kaleidoscope_var.get(),
            "gauss_glow": self.gauss_glow_var.get(),
            "vignette": self.vignette_var.get(),
        }

    def get_pattern_name(self):
        return self.pattern_var.get()
