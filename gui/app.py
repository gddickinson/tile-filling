"""Main application window for tile-filling visualizer."""

import json
import os
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk

from patterns import PATTERN_REGISTRY
from gui.controls import ControlPanel
from rendering.renderer import render_to_image, render_high_res

EFFECT_KEYS = ["kaleidoscope", "gauss_glow", "vignette", "chromatic", "scanlines", "grain"]
PRESETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "presets")


class TileFillingApp:
    """Main GUI application."""

    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 800

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tile Filling Visualizer")
        self.root.configure(bg="#2d2d2d")

        self._update_pending = False
        self._current_image = None
        self._photo = None

        os.makedirs(PRESETS_DIR, exist_ok=True)

        self._build_ui()
        self._bind_keys()
        self._init_pattern()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#2d2d2d")
        style.configure("TLabelframe", background="#2d2d2d", foreground="#cccccc")
        style.configure("TLabelframe.Label", background="#2d2d2d", foreground="#cccccc")
        style.configure("TLabel", background="#2d2d2d", foreground="#cccccc")
        style.configure("TCheckbutton", background="#2d2d2d", foreground="#cccccc")
        style.configure("TButton", padding=5)

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        # Canvas area
        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(
            canvas_frame, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT,
            bg="#1a1a2e", highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        # Scrollable control panel (right side)
        panel_frame = ttk.Frame(main, width=260)
        panel_frame.pack(side="right", fill="y", padx=5, pady=5)
        panel_frame.pack_propagate(False)

        panel_canvas = tk.Canvas(panel_frame, bg="#2d2d2d", highlightthickness=0, width=240)
        scrollbar = ttk.Scrollbar(panel_frame, orient="vertical", command=panel_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        panel_canvas.pack(side="left", fill="both", expand=True)
        panel_canvas.configure(yscrollcommand=scrollbar.set)

        pattern_names = list(PATTERN_REGISTRY.keys())
        self.controls = ControlPanel(panel_canvas, pattern_names, self._on_change)
        panel_canvas.create_window((0, 0), window=self.controls, anchor="nw")

        def _on_frame_configure(e):
            panel_canvas.configure(scrollregion=panel_canvas.bbox("all"))
        self.controls.bind("<Configure>", _on_frame_configure)

        # Enable mousewheel scrolling on the panel
        def _on_mousewheel(event):
            panel_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        panel_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Buttons
        btn_frame = ttk.Frame(self.controls)
        btn_frame.pack(fill="x", pady=(15, 0))

        ttk.Button(btn_frame, text="Randomize All", command=self._randomize).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Regenerate", command=self._regenerate).pack(fill="x", pady=2)

        preset_row = ttk.Frame(btn_frame)
        preset_row.pack(fill="x", pady=2)
        ttk.Button(preset_row, text="Save Preset", command=self._save_preset).pack(side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(preset_row, text="Load Preset", command=self._load_preset).pack(side="right", fill="x", expand=True, padx=(2, 0))

        ttk.Button(btn_frame, text="Export PNG", command=self._export_png).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Export Hi-Res PNG", command=self._export_hires).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Batch Random (10x)", command=self._batch_export).pack(fill="x", pady=2)

        # Status bar with keyboard hints
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready  |  R=Regen  Space=Randomize  E=Export  S=Save Preset")
        ttk.Label(status_frame, textvariable=self.status_var, relief="sunken", padding=2).pack(fill="x")

    def _bind_keys(self):
        """Bind keyboard shortcuts."""
        self.root.bind("r", lambda e: self._regenerate())
        self.root.bind("<space>", lambda e: self._randomize())
        self.root.bind("e", lambda e: self._export_png())
        self.root.bind("s", lambda e: self._save_preset())
        self.root.bind("l", lambda e: self._load_preset())

    def _init_pattern(self):
        name = self.controls.get_pattern_name()
        pattern_cls = PATTERN_REGISTRY[name]
        self.current_pattern = pattern_cls()
        self.controls.build_params(pattern_cls.get_params())
        self._schedule_update()

    def _on_change(self, change_type):
        if change_type == "pattern":
            name = self.controls.get_pattern_name()
            pattern_cls = PATTERN_REGISTRY[name]
            self.current_pattern = pattern_cls()
            self.controls.build_params(pattern_cls.get_params())
        self._schedule_update()

    def _schedule_update(self):
        if not self._update_pending:
            self._update_pending = True
            self.root.after(50, self._do_update)

    def _do_update(self):
        self._update_pending = False
        self._render()

    def _on_resize(self, event):
        self.CANVAS_WIDTH = event.width
        self.CANVAS_HEIGHT = event.height
        self._schedule_update()

    def _get_effects(self, settings):
        return {k: settings.get(k, False) for k in EFFECT_KEYS}

    def _render(self):
        params = self.controls.get_params()
        settings = self.controls.get_render_settings()
        w, h = self.CANVAS_WIDTH, self.CANVAS_HEIGHT

        self.status_var.set("Rendering...")
        self.root.update_idletasks()

        try:
            commands = self.current_pattern.generate(w, h, params)
            self.status_var.set(f"Drawing {len(commands)} elements...")
            self.root.update_idletasks()

            img = render_to_image(
                commands, w, h,
                palette_name=settings["palette"],
                line_width=settings["line_width"],
                glow=settings["glow"],
                gradient=settings["gradient"],
                **self._get_effects(settings),
            )

            self._current_image = img
            self._photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self._photo)
            self.status_var.set(f"Done - {len(commands)} elements  |  R=Regen  Space=Randomize  E=Export")

        except Exception as e:
            self.status_var.set(f"Error: {e}")
            import traceback
            traceback.print_exc()

    def _regenerate(self):
        self._render()

    def _randomize(self):
        """Randomize all pattern parameters."""
        name = self.controls.get_pattern_name()
        pattern_cls = PATTERN_REGISTRY[name]
        param_defs = pattern_cls.get_params()

        for pdef in param_defs:
            pname = pdef["name"]
            if pname not in self.controls.param_vars:
                continue
            var = self.controls.param_vars[pname]
            ptype = pdef["type"]

            if ptype == "int":
                val = random.randint(pdef["min"], pdef["max"])
                var.set(val)
                lk = pname + "_label"
                if lk in self.controls.param_widgets:
                    self.controls.param_widgets[lk].config(text=str(val))
            elif ptype == "float":
                val = pdef["min"] + random.random() * (pdef["max"] - pdef["min"])
                var.set(val)
                lk = pname + "_label"
                if lk in self.controls.param_widgets:
                    self.controls.param_widgets[lk].config(text=f"{val:.2f}")
            elif ptype == "bool":
                var.set(random.choice([True, False]))

        # Also randomize palette
        from rendering.colors import PALETTES
        palettes = list(PALETTES.keys())
        self.controls.palette_var.set(random.choice(palettes))

        self._schedule_update()

    def _save_preset(self):
        """Save current settings as a JSON preset."""
        path = filedialog.asksaveasfilename(
            initialdir=PRESETS_DIR, defaultextension=".json",
            filetypes=[("JSON files", "*.json")], title="Save Preset",
        )
        if not path:
            return

        preset = {
            "pattern": self.controls.get_pattern_name(),
            "params": self.controls.get_params(),
            "settings": self.controls.get_render_settings(),
        }
        with open(path, "w") as f:
            json.dump(preset, f, indent=2)
        self.status_var.set(f"Preset saved: {os.path.basename(path)}")

    def _load_preset(self):
        """Load a JSON preset."""
        path = filedialog.askopenfilename(
            initialdir=PRESETS_DIR, defaultextension=".json",
            filetypes=[("JSON files", "*.json")], title="Load Preset",
        )
        if not path:
            return

        with open(path) as f:
            preset = json.load(f)

        # Set pattern
        pattern_name = preset.get("pattern", "Grid")
        if pattern_name in PATTERN_REGISTRY:
            self.controls.pattern_var.set(pattern_name)
            pattern_cls = PATTERN_REGISTRY[pattern_name]
            self.current_pattern = pattern_cls()
            self.controls.build_params(pattern_cls.get_params())

        # Set params
        for name, value in preset.get("params", {}).items():
            if name in self.controls.param_vars:
                self.controls.param_vars[name].set(value)
                lk = name + "_label"
                if lk in self.controls.param_widgets:
                    if isinstance(value, float):
                        self.controls.param_widgets[lk].config(text=f"{value:.2f}")
                    else:
                        self.controls.param_widgets[lk].config(text=str(value))

        # Set render settings
        s = preset.get("settings", {})
        if "palette" in s:
            self.controls.palette_var.set(s["palette"])
        if "line_width" in s:
            self.controls.line_width_var.set(s["line_width"])
        if "glow" in s:
            self.controls.glow_var.set(s["glow"])
        if "gradient" in s:
            self.controls.gradient_var.set(s["gradient"])

        self.status_var.set(f"Loaded preset: {os.path.basename(path)}")
        self._schedule_update()

    def _export_png(self):
        if self._current_image is None:
            messagebox.showwarning("Export", "Nothing to export yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Export PNG",
        )
        if path:
            self._current_image.save(path)
            self.status_var.set(f"Exported to {path}")

    def _export_hires(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Export Hi-Res PNG",
        )
        if not path:
            return

        self.status_var.set("Rendering hi-res (4x)...")
        self.root.update_idletasks()

        params = self.controls.get_params()
        settings = self.controls.get_render_settings()
        w, h = self.CANVAS_WIDTH, self.CANVAS_HEIGHT

        try:
            commands = self.current_pattern.generate(w, h, params)
            img = render_high_res(
                commands, w, h,
                palette_name=settings["palette"],
                line_width=settings["line_width"],
                glow=settings["glow"],
                gradient=settings["gradient"],
                **self._get_effects(settings),
            )
            img.save(path, dpi=(300, 300))
            self.status_var.set(f"Hi-res exported to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _batch_export(self):
        """Generate 10 random variations and save to a folder."""
        folder = filedialog.askdirectory(title="Select folder for batch export")
        if not folder:
            return

        name = self.controls.get_pattern_name()
        pattern_cls = PATTERN_REGISTRY[name]

        for i in range(10):
            self.status_var.set(f"Batch rendering {i + 1}/10...")
            self.root.update_idletasks()

            # Randomize params
            params = {}
            for pdef in pattern_cls.get_params():
                ptype = pdef["type"]
                if ptype == "int":
                    params[pdef["name"]] = random.randint(pdef["min"], pdef["max"])
                elif ptype == "float":
                    params[pdef["name"]] = pdef["min"] + random.random() * (pdef["max"] - pdef["min"])
                elif ptype == "bool":
                    params[pdef["name"]] = random.choice([True, False])

            from rendering.colors import PALETTES
            palette = random.choice(list(PALETTES.keys()))

            p = pattern_cls()
            w, h = self.CANVAS_WIDTH, self.CANVAS_HEIGHT
            commands = p.generate(w, h, params)
            img = render_to_image(commands, w, h, palette_name=palette, line_width=1.0)
            img.save(os.path.join(folder, f"{name}_{i:02d}.png"))

        self.status_var.set(f"Batch exported 10 images to {folder}")

    def run(self):
        self.root.mainloop()
