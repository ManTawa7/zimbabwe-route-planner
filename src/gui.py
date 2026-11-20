import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional

import tkintermapview

from src.graph import RoadGraph
from src.search import SearchOutcome, search_route


class ZimbabweRoutePlannerGUI:
    def __init__(self, root: tk.Tk, graph: RoadGraph) -> None:
        self.root = root
        self.graph = graph
        self.root.title("Zimbabwe Route Planner (A* & UCS/BFS)")
        self.root.geometry("1200x760")

        self.route_path_obj = None
        self.explored_markers: List = []
        self.route_markers: List = []

        self._build_layout()
        self._plot_all_towns()

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left control panel
        controls = ttk.Frame(self.root, padding=14, width=340)
        controls.grid(row=0, column=0, sticky="ns")
        controls.grid_propagate(False)

        ttk.Label(
            controls,
            text="Zimbabwe Route Planner",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        town_names = sorted(self.graph.towns.keys())
        default_start = "Harare" if "Harare" in town_names else town_names[0]
        default_goal = "Bulawayo" if "Bulawayo" in town_names else town_names[-1]

        ttk.Label(controls, text="Start Town:").pack(anchor="w")
        self.start_var = tk.StringVar(value=default_start)
        self.start_combo = ttk.Combobox(
            controls, textvariable=self.start_var, values=town_names, state="readonly"
        )
        self.start_combo.pack(fill="x", pady=(2, 10))

        ttk.Label(controls, text="Destination Town:").pack(anchor="w")
        self.goal_var = tk.StringVar(value=default_goal)
        self.goal_combo = ttk.Combobox(
            controls, textvariable=self.goal_var, values=town_names, state="readonly"
        )
        self.goal_combo.pack(fill="x", pady=(2, 12))

        ttk.Label(controls, text="Optimization Criterion:").pack(anchor="w")
        self.mode_var = tk.StringVar(value="distance")
        ttk.Radiobutton(
            controls,
            text="Shortest Distance (A* + Haversine)",
            variable=self.mode_var,
            value="distance",
        ).pack(anchor="w", pady=(4, 2))
        ttk.Radiobutton(
            controls,
            text="Fewest Stops (UCS / BFS)",
            variable=self.mode_var,
            value="stops",
        ).pack(anchor="w", pady=(0, 10))

        self.show_explored_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls,
            text="Show explored intermediate nodes",
            variable=self.show_explored_var,
        ).pack(anchor="w", pady=(0, 12))

        btn_row = ttk.Frame(controls)
        btn_row.pack(fill="x", pady=(0, 14))
        ttk.Button(btn_row, text="Find Route", command=self.on_find_route).pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(btn_row, text="Clear Map", command=self.clear_route_overlay).pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

        ttk.Separator(controls, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(
            controls, text="Search Metrics & Route", font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))

        self.stats_text = tk.Text(
            controls, height=18, wrap="word", state="disabled", font=("Consolas", 9)
        )
        self.stats_text.pack(fill="both", expand=True)

        # Right map view
        self.map_widget = tkintermapview.TkinterMapView(
            self.root, corner_radius=0
        )
        self.map_widget.grid(row=0, column=1, sticky="nsew")
        self.map_widget.set_position(-19.0154, 29.1549)
        self.map_widget.set_zoom(6)

    def _plot_all_towns(self) -> None:
        for town in self.graph.towns.values():
            self.map_widget.set_marker(
                town.lat,
                town.lon,
                text=town.name,
                marker_color_circle="#1f4e78",
                marker_color_outside="#4a89dc",
            )

    def clear_route_overlay(self) -> None:
        if self.route_path_obj is not None:
            self.route_path_obj.delete()
            self.route_path_obj = None

        for marker in self.explored_markers + self.route_markers:
            marker.delete()
        self.explored_markers.clear()
        self.route_markers.clear()

    def _set_stats(self, content: str) -> None:
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, content)
        self.stats_text.configure(state="disabled")

    def on_find_route(self) -> None:
        start = self.start_var.get()
        goal = self.goal_var.get()
        mode = self.mode_var.get()

        if not start or not goal:
            messagebox.showwarning("Missing Input", "Please select both start and destination towns.")
            return

        use_heuristic = mode == "distance"
        outcome: Optional[SearchOutcome] = search_route(
            self.graph,
            start=start,
            goal=goal,
            mode=mode,
            use_heuristic=use_heuristic,
        )

        self.clear_route_overlay()

        if outcome is None:
            messagebox.showinfo("No Route", f"No path found from {start} to {goal}.")
            return

        if self.show_explored_var.get():
            for town_name in outcome.explored_nodes:
                if town_name not in outcome.path:
                    t = self.graph.towns[town_name]
                    m = self.map_widget.set_marker(
                        t.lat,
                        t.lon,
                        text=f"Visited: {t.name}",
                        marker_color_circle="#b7791f",
                        marker_color_outside="#ecc94b",
                    )
                    self.explored_markers.append(m)

        coords = [
            (self.graph.towns[name].lat, self.graph.towns[name].lon)
            for name in outcome.path
        ]
        if len(coords) >= 2:
            self.route_path_obj = self.map_widget.set_path(
                coords, color="#198754", width=4
            )

        for idx, town_name in enumerate(outcome.path):
            t = self.graph.towns[town_name]
            label = f"{idx + 1}. {town_name}"
            m = self.map_widget.set_marker(
                t.lat,
                t.lon,
                text=label,
                marker_color_circle="#146c43",
                marker_color_outside="#20c997",
            )
            self.route_markers.append(m)

        self.map_widget.set_position(
            self.graph.towns[start].lat, self.graph.towns[start].lon
        )
        self.map_widget.set_zoom(7)

        summary = (
            f"Algorithm : {outcome.algorithm}\n"
            f"Mode      : {outcome.mode}\n"
            f"Distance  : {outcome.total_distance_km} km\n"
            f"Stops     : {outcome.total_stops}\n"
            f"Expanded  : {outcome.nodes_expanded} nodes\n"
            f"Max Front : {outcome.max_frontier_size}\n"
            f"Runtime   : {outcome.execution_time_ms} ms\n\n"
            f"Route ({len(outcome.path)} towns):\n"
            + " -> ".join(outcome.path)
        )
        self._set_stats(summary)


def main() -> None:
    graph = RoadGraph.from_json("data/zimbabwe_graph.json")
    root = tk.Tk()
    ZimbabweRoutePlannerGUI(root, graph)
    root.mainloop()


if __name__ == "__main__":
    main()
