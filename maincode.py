import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import math

class MapsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campus Map Navigation")
        self.root.geometry("800x700")

        self.places = [
            "Gate", "EEE Block", "MBA & Mechanical Block", "First Year Block",
            "Boys Hostel", "Main Block", "Canteen", "Einstein Block"
        ]

        self.positions = {
            "Gate": (100, 300),
            "EEE Block": (200, 500),
            "MBA & Mechanical Block": (350, 550),
            "First Year Block": (550, 500),
            "Boys Hostel": (600, 400),
            "Main Block": (500, 300),
            "Canteen": (400, 100),
            "Einstein Block": (250, 100)
        }

        self.graph = self.build_graph()
        self.create_widgets()

    def build_graph(self):
        connections = {
            "Gate": ["EEE Block", "Einstein Block","Main Block"],
            "EEE Block": ["Gate", "MBA & Mechanical Block","First Year Block"],
            "MBA & Mechanical Block": ["EEE Block", "First Year Block"],
            "First Year Block": ["MBA & Mechanical Block", "Boys Hostel"],
            "Boys Hostel": ["First Year Block", "Main Block","EEE Block"],
            "Main Block": ["Boys Hostel", "Canteen", "Einstein Block"],
            "Canteen": ["Main Block", "Einstein Block"],
            "Einstein Block": ["Gate", "Main Block", "Canteen"]
        }

        graph = {place: [] for place in self.places}
        for place, neighbors in connections.items():
            for neighbor in neighbors:
                x1, y1 = self.positions[place]
                x2, y2 = self.positions[neighbor]
                dist = math.hypot(x2 - x1, y2 - y1)
                graph[place].append((neighbor, dist))
        return graph

    def create_widgets(self):
        tk.Label(self.root, text="AVS ENGINEERING COLLEGE MAP NAVIGATION", font=("Arial", 18, "bold")).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="From:").grid(row=0, column=0, padx=5)
        self.source = ttk.Combobox(frame, values=self.places, width=25)
        self.source.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="To:").grid(row=0, column=2, padx=5)
        self.dest = ttk.Combobox(frame, values=self.places, width=25)
        self.dest.grid(row=0, column=3, padx=5)

        tk.Button(frame, text="Find Route", command=self.find_route, bg="lightblue").grid(row=0, column=4, padx=10)

        self.canvas = tk.Canvas(self.root, width=700, height=600, bg="white", relief="solid", bd=1)
        self.canvas.pack(pady=10)

        self.route_info = tk.Text(self.root, height=6, width=90)
        self.route_info.pack(pady=10)

        self.draw_map()

    def draw_map(self):
        self.canvas.delete("all")

        for place in self.places:
            for neighbor, _ in self.graph[place]:
                x1, y1 = self.positions[place]
                x2, y2 = self.positions[neighbor]
                self.canvas.create_line(x1, y1, x2, y2, fill="lightgray")

        for place, (x, y) in self.positions.items():
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="red", outline="black")
            self.canvas.create_text(x, y - 15, text=place, font=("Arial", 9, "bold"))

    def dijkstra(self, start, end):
        queue = [(0, start, [])]
        visited = set()
        while queue:
            cost, node, path = heapq.heappop(queue)
            if node in visited:
                continue
            visited.add(node)
            path = path + [node]
            if node == end:
                return cost, path
            for neighbor, weight in self.graph[node]:
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + weight, neighbor, path))
        return float("inf"), []

    def find_route(self):
        src = self.source.get()
        dst = self.dest.get()

        if not src or not dst:
            messagebox.showwarning("Warning", "Please select both source and destination!")
            return

        if src == dst:
            messagebox.showinfo("Info", "Source and destination are the same!")
            return

        self.draw_map()
        distance, path = self.dijkstra(src, dst)

        for i in range(len(path) - 1):
            x1, y1 = self.positions[path[i]]
            x2, y2 = self.positions[path[i + 1]]
            self.canvas.create_line(x1, y1, x2, y2, width=4, fill="blue", tags="route")

        self.route_info.delete(1.0, tk.END)
        route_text = f"Shortest Path: {' → '.join(path)}\n"
        route_text += f"Total Distance: {int(distance)} units\n"
        route_text += f"Estimated Time: {int(distance / 3)} minutes\n"
        route_text += "Path calculated using Dijkstra's Algorithm."
        self.route_info.insert(tk.END, route_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MapsApp(root)
    root.mainloop()
