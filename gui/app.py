"""Main application window for tile-filling visualizer."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk

from patterns import PATTERN_REGISTRY
from gui.controls import ControlPanel
from rendering.renderer import render_to_image, render_high_res


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

        self._build_ui()
        self._init_pattern()

    def _build_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#2d2d2d")
        style.configure("TLabelframe", background="#2d2d2d", foreground="#cccccc")
        style.configure("TLabelframe.Label", background="#2d2d2d", foreground="#cccccc")
        style.configure("TLabel", background="#2d2d2d", foreground="#cccccc")
        style.configure("TCheckbutton", background="#2d2d2d", foreground="#cccccc")
        style.configure("TButton", padding=5)

        # Main layout
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        # Canvas area
        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg="#1a1a2e",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        # Control panel (right side)
        pattern_names = list(PATTERN_REGISTRY.keys())
        self.controls = ControlPanel(main, pattern_names, self._on_change)
        self.controls.pack(side="right", fill="y", padx=5, pady=5)

        # Buttons at bottom of controls
        btn_frame = ttk.Frame(self.controls)
        btn_frame.pack(fill="x", pady=(15, 0))

        ttk.Button(btn_frame, text="Regenerate", command=self._regenerate).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Export PNG", command=self._export_png).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Export Hi-Res PNG", command=self._export_hires).pack(fill="x", pady=2)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", padding=2)
        status.pack(fill="x", side="bottom")

    def _init_pattern(self):
        """Initialize with the first pattern."""
        name = self.controls.get_pattern_name()
        pattern_cls = PATTERN_REGISTRY[name]
        self.current_pattern = pattern_cls()
        self.controls.build_params(pattern_cls.get_params())
        self._schedule_update()

    def _on_change(self, change_type):
        """Handle any parameter change."""
        if change_type == "pattern":
            name = self.controls.get_pattern_name()
            pattern_cls = PATTERN_REGISTRY[name]
            self.current_pattern = pattern_cls()
            self.controls.build_params(pattern_cls.get_params())

        self._schedule_update()

    def _schedule_update(self):
        """Debounce updates to avoid rendering on every slider tick."""
        if not self._update_pending:
            self._update_pending = True
            self.root.after(50, self._do_update)

    def _do_update(self):
        """Actually perform the render update."""
        self._update_pending = False
        self._render()

    def _on_resize(self, event):
        self.CANVAS_WIDTH = event.width
        self.CANVAS_HEIGHT = event.height
        self._schedule_update()

    def _render(self):
        """Render the current pattern to the canvas."""
        params = self.controls.get_params()
        settings = self.controls.get_render_settings()

        w = self.CANVAS_WIDTH
        h = self.CANVAS_HEIGHT

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
                kaleidoscope=settings.get("kaleidoscope", 0),
                gauss_glow=settings.get("gauss_glow", False),
                vignette=settings.get("vignette", False),
            )

            self._current_image = img
            self._photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self._photo)

            self.status_var.set(f"Done - {len(commands)} elements rendered")

        except Exception as e:
            self.status_var.set(f"Error: {e}")
            import traceback
            traceback.print_exc()

    def _regenerate(self):
        """Force regeneration (useful for random-seed patterns)."""
        self._render()

    def _export_png(self):
        """Export current view as PNG."""
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
        """Export at 4x resolution."""
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
        w = self.CANVAS_WIDTH
        h = self.CANVAS_HEIGHT

        try:
            commands = self.current_pattern.generate(w, h, params)
            img = render_high_res(
                commands, w, h,
                palette_name=settings["palette"],
                line_width=settings["line_width"],
                glow=settings["glow"],
                gradient=settings["gradient"],
                kaleidoscope=settings.get("kaleidoscope", 0),
                gauss_glow=settings.get("gauss_glow", False),
                vignette=settings.get("vignette", False),
            )
            img.save(path, dpi=(300, 300))
            self.status_var.set(f"Hi-res exported to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def run(self):
        self.root.mainloop()
