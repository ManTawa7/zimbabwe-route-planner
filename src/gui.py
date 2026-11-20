import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional

import tkintermapview

from src.graph import RoadGraph
from src.search import SearchResult, find_route


class RoutePlannerApp:
    BG_DARK = "#0f172a"
    PANEL_BG = "#111827"
    CARD_BG = "#1e293b"
    TEXT_PRIMARY = "#f8fafc"
    TEXT_MUTED = "#94a3b8"
    ACCENT = "#10b981"
    ACCENT_HOVER = "#059669"
    BORDER = "#334155"

    def __init__(self, root: tk.Tk, graph: RoadGraph) -> None:
        self.root = root
        self.graph = graph
        self.root.title("Zimbabwe Route Planner — AI Search & Map")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 680)
        self.root.configure(bg=self.BG_DARK)

        self.route_line = None
        self.visited_markers: List = []
        self.path_markers: List = []

        self._configure_styles()
        self._build_ui()
        self._draw_town_pins()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("App.TFrame", background=self.PANEL_BG)
        style.configure("Card.TFrame", background=self.CARD_BG)

        style.configure(
            "Title.TLabel",
            background=self.PANEL_BG,
            foreground=self.TEXT_PRIMARY,
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.PANEL_BG,
            foreground=self.TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Field.TLabel",
            background=self.PANEL_BG,
            foreground=self.TEXT_PRIMARY,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "CardTitle.TLabel",
            background=self.CARD_BG,
            foreground=self.TEXT_MUTED,
            font=("Segoe UI", 8, "bold"),
        )
        style.configure(
            "CardValue.TLabel",
            background=self.CARD_BG,
            foreground=self.TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "Accent.TLabel",
            background=self.CARD_BG,
            foreground=self.ACCENT,
            font=("Segoe UI", 12, "bold"),
        )

        style.configure(
            "Modern.TCombobox",
            fieldbackground=self.CARD_BG,
            background=self.CARD_BG,
            foreground=self.TEXT_PRIMARY,
            arrowcolor=self.TEXT_PRIMARY,
            bordercolor=self.BORDER,
            padding=6,
        )
        style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", self.CARD_BG)],
            foreground=[("readonly", self.TEXT_PRIMARY)],
        )

        style.configure(
            "Modern.TRadiobutton",
            background=self.PANEL_BG,
            foreground=self.TEXT_PRIMARY,
            font=("Segoe UI", 9),
            padding=4,
        )
        style.map(
            "Modern.TRadiobutton",
            background=[("active", self.PANEL_BG)],
            foreground=[("active", self.ACCENT)],
        )

        style.configure(
            "Modern.TCheckbutton",
            background=self.PANEL_BG,
            foreground=self.TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        style.map(
            "Modern.TCheckbutton",
            background=[("active", self.PANEL_BG)],
            foreground=[("active", self.TEXT_PRIMARY)],
        )

        style.configure(
            "Primary.TButton",
            background=self.ACCENT,
            foreground="#06281e",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=9,
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.ACCENT_HOVER), ("pressed", self.ACCENT_HOVER)],
        )

        style.configure(
            "Secondary.TButton",
            background=self.CARD_BG,
            foreground=self.TEXT_PRIMARY,
            font=("Segoe UI", 9, "bold"),
            bordercolor=self.BORDER,
            padding=8,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", self.BORDER)],
        )

    def _build_ui(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self.root, style="App.TFrame", padding=18, width=370)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ttk.Label(sidebar, text="Zimbabwe Route Planner", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            sidebar,
            text="A* Shortest Distance & Fewest Stops Search",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 16))

        towns = sorted(self.graph.towns.keys())
        default_start = "Harare" if "Harare" in towns else towns[0]
        default_goal = "Bulawayo" if "Bulawayo" in towns else towns[-1]

        ttk.Label(sidebar, text="ORIGIN TOWN", style="Field.TLabel").pack(anchor="w")
        self.start_var = tk.StringVar(value=default_start)
        ttk.Combobox(
            sidebar,
            textvariable=self.start_var,
            values=towns,
            state="readonly",
            style="Modern.TCombobox",
        ).pack(fill="x", pady=(4, 8))

        swap_row = ttk.Frame(sidebar, style="App.TFrame")
        swap_row.pack(fill="x", pady=(0, 6))
        ttk.Button(
            swap_row,
            text="⇅ Swap Origin & Destination",
            command=self._swap_towns,
            style="Secondary.TButton",
        ).pack(fill="x")

        ttk.Label(sidebar, text="DESTINATION TOWN", style="Field.TLabel").pack(anchor="w", pady=(4, 0))
        self.goal_var = tk.StringVar(value=default_goal)
        ttk.Combobox(
            sidebar,
            textvariable=self.goal_var,
            values=towns,
            state="readonly",
            style="Modern.TCombobox",
        ).pack(fill="x", pady=(4, 14))

        ttk.Label(sidebar, text="SEARCH STRATEGY", style="Field.TLabel").pack(anchor="w")
        self.mode_var = tk.StringVar(value="distance")
        ttk.Radiobutton(
            sidebar,
            text="Shortest Distance — A* (Haversine km)",
            variable=self.mode_var,
            value="distance",
            style="Modern.TRadiobutton",
        ).pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(
            sidebar,
            text="Fewest Stops — UCS / BFS (Town Hops)",
            variable=self.mode_var,
            value="stops",
            style="Modern.TRadiobutton",
        ).pack(anchor="w", pady=(0, 10))

        self.show_visited_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sidebar,
            text="Show explored towns on map",
            variable=self.show_visited_var,
            style="Modern.TCheckbutton",
        ).pack(anchor="w", pady=(0, 14))

        action_row = ttk.Frame(sidebar, style="App.TFrame")
        action_row.pack(fill="x", pady=(0, 16))
        action_row.columnconfigure(0, weight=2)
        action_row.columnconfigure(1, weight=1)

        ttk.Button(
            action_row,
            text="Find Route",
            command=self.run_search,
            style="Primary.TButton",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            action_row,
            text="Clear",
            command=self.clear_overlay,
            style="Secondary.TButton",
        ).grid(row=0, column=1, sticky="ew")

        # 2x2 Metric Cards
        cards_grid = ttk.Frame(sidebar, style="App.TFrame")
        cards_grid.pack(fill="x", pady=(0, 14))
        cards_grid.columnconfigure(0, weight=1)
        cards_grid.columnconfigure(1, weight=1)

        self.dist_lbl = self._create_metric_card(cards_grid, 0, 0, "DISTANCE", "-- km", accent=True)
        self.stops_lbl = self._create_metric_card(cards_grid, 0, 1, "STOPS", "--")
        self.expanded_lbl = self._create_metric_card(cards_grid, 1, 0, "EXPANDED", "--")
        self.time_lbl = self._create_metric_card(cards_grid, 1, 1, "RUNTIME", "-- ms")

        ttk.Label(sidebar, text="ROUTE BREAKDOWN", style="Field.TLabel").pack(anchor="w", pady=(0, 4))

        self.output_box = tk.Text(
            sidebar,
            height=10,
            wrap="word",
            state="disabled",
            bg=self.CARD_BG,
            fg=self.TEXT_PRIMARY,
            insertbackground=self.TEXT_PRIMARY,
            relief="flat",
            padx=10,
            pady=8,
            font=("Consolas", 9),
        )
        self.output_box.pack(fill="both", expand=True)

        self.map_view = tkintermapview.TkinterMapView(self.root, corner_radius=0)
        self.map_view.grid(row=0, column=1, sticky="nsew")
        self.map_view.set_position(-19.0154, 29.1549)
        self.map_view.set_zoom(6)

    def _create_metric_card(
        self,
        parent: ttk.Frame,
        row: int,
        col: int,
        title: str,
        initial_value: str,
        accent: bool = False,
    ) -> ttk.Label:
        card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        pad_x = (0, 5) if col == 0 else (5, 0)
        pad_y = (0, 6) if row == 0 else (4, 0)
        card.grid(row=row, column=col, sticky="nsew", padx=pad_x, pady=pad_y)

        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        val_style = "Accent.TLabel" if accent else "CardValue.TLabel"
        val_lbl = ttk.Label(card, text=initial_value, style=val_style)
        val_lbl.pack(anchor="w", pady=(2, 0))
        return val_lbl

    def _swap_towns(self) -> None:
        origin = self.start_var.get()
        dest = self.goal_var.get()
        self.start_var.set(dest)
        self.goal_var.set(origin)

    def _draw_town_pins(self) -> None:
        for town in self.graph.towns.values():
            self.map_view.set_marker(
                town.lat,
                town.lon,
                text=town.name,
                marker_color_circle="#1e3a8a",
                marker_color_outside="#60a5fa",
            )

    def clear_overlay(self) -> None:
        if self.route_line is not None:
            self.route_line.delete()
            self.route_line = None

        for marker in self.visited_markers + self.path_markers:
            marker.delete()
        self.visited_markers.clear()
        self.path_markers.clear()

        self.dist_lbl.configure(text="-- km")
        self.stops_lbl.configure(text="--")
        self.expanded_lbl.configure(text="--")
        self.time_lbl.configure(text="-- ms")
        self._write_output("Select an origin and destination, then click Find Route.")

    def _write_output(self, text: str) -> None:
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)
        self.output_box.configure(state="disabled")

    def run_search(self) -> None:
        start = self.start_var.get()
        goal = self.goal_var.get()
        mode = self.mode_var.get()

        if not start or not goal:
            messagebox.showwarning("Missing Selection", "Choose both an origin and destination town.")
            return

        result: Optional[SearchResult] = find_route(
            self.graph,
            start=start,
            goal=goal,
            mode=mode,
            use_heuristic=(mode == "distance"),
        )

        self.clear_overlay()

        if result is None:
            messagebox.showinfo("No Route", f"No path found from {start} to {goal}.")
            return

        if self.show_visited_var.get():
            for town_name in result.explored:
                if town_name not in result.path:
                    t = self.graph.towns[town_name]
                    m = self.map_view.set_marker(
                        t.lat,
                        t.lon,
                        text=f"Explored: {t.name}",
                        marker_color_circle="#b45309",
                        marker_color_outside="#fbbf24",
                    )
                    self.visited_markers.append(m)

        coords = [(self.graph.towns[name].lat, self.graph.towns[name].lon) for name in result.path]
        if len(coords) >= 2:
            self.route_line = self.map_view.set_path(coords, color="#10b981", width=5)

        for i, town_name in enumerate(result.path):
            t = self.graph.towns[town_name]
            m = self.map_view.set_marker(
                t.lat,
                t.lon,
                text=f"{i + 1}. {town_name}",
                marker_color_circle="#047857",
                marker_color_outside="#34d399",
            )
            self.path_markers.append(m)

        self.map_view.set_position(self.graph.towns[start].lat, self.graph.towns[start].lon)
        self.map_view.set_zoom(7)

        self.dist_lbl.configure(text=f"{result.distance_km:.1f} km")
        self.stops_lbl.configure(text=str(result.stops))
        self.expanded_lbl.configure(text=f"{result.nodes_expanded} (max {result.max_frontier})")
        self.time_lbl.configure(text=f"{result.runtime_ms:.2f} ms")

        steps = "\n".join(f"{idx + 1}. {name}" for idx, name in enumerate(result.path))
        summary = (
            f"Algorithm: {result.algorithm}\n"
            f"Path ({len(result.path)} towns):\n"
            f"{steps}"
        )
        self._write_output(summary)


def main() -> None:
    graph = RoadGraph.from_json("data/zimbabwe_graph.json")
    root = tk.Tk()
    RoutePlannerApp(root, graph)
    root.mainloop()


if __name__ == "__main__":
    main()