from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

places = [
    "Gate", "EEE Block", "MBA & Mechanical Block", "First Year Block",
    "Boys Hostel", "Main Block", "Canteen", "Einstein Block"
]

positions = {
    "Gate": (100, 300),
    "EEE Block": (200, 500),
    "MBA & Mechanical Block": (350, 550),
    "First Year Block": (550, 500),
    "Boys Hostel": (600, 400),
    "Main Block": (500, 300),
    "Canteen": (400, 100),
    "Einstein Block": (250, 100)
}

connections = {
    "Gate": ["EEE Block", "Einstein Block","Main Block"],
    "EEE Block": ["Gate", "MBA & Mechanical Block","First Year Block"],
    "MBA & Mechanical Block": ["EEE Block", "First Year Block"],
    "First Year Block": ["MBA & Mechanical Block", "Boys Hostel"],
    "Boys Hostel": ["First Year Block", "Main Block"],
    "Main Block": ["Boys Hostel", "Canteen", "Einstein Block"],
    "Canteen": ["Main Block", "Einstein Block"],
    "Einstein Block": ["Gate", "Main Block", "Canteen"]
}

# Example images URLs or local static paths (replace with your own images or URLs)
images = {
    "Gate": "/static/images/gate.jpg",
    "EEE Block": "/static/images/eee_block.jpg",
    "MBA & Mechanical Block": "/static/images/mba_mechanical_block.jpg",
    "First Year Block": "/static/images/first_year_block.jpg",
    "Boys Hostel": "/static/images/boys_hostel.jpg",
    "Main Block": "/static/images/main_block.jpg",
    "Canteen": "/static/images/canteen.jpg",
    "Einstein Block": "/static/images/einstein_block.jpg"
}


INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Campus Map Navigation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f9f9f9; }
        header { text-align: center; padding: 20px; background-color: #003366; color: white; font-size: 24px; font-weight: bold; }
        #map-container { display: flex; justify-content: center; margin-top: 20px; }
        canvas { border: 1px solid #ccc; background: white; }
        #info {
            margin: 20px auto; 
            width: 90vw; 
            max-width: 700px; 
            background: white; 
            padding: 15px; 
            border-radius: 6px; 
            box-shadow: 0 0 5px rgba(0,0,0,0.2);
            text-align: center;
        }
        #node-image {
            max-width: 100%; 
            height: auto; 
            margin-top: 15px;
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(0,0,0,0.15);
        }
        #select-container {
            text-align: center;
            margin: 10px 0;
        }
        select {
            font-size: 16px;
            padding: 5px 10px;
            margin: 0 10px;
        }
        button {
            font-size: 16px;
            padding: 6px 12px;
            background: #007BFF;
            border: none;
            color: white;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <header>AVS ENGINEERING COLLEGE MAP NAVIGATION</header>

    <div id="select-container">
        <label for="source">From: </label>
        <select id="source">
            <option value="">Select source</option>
            {% for place in places %}
            <option value="{{ place }}">{{ place }}</option>
            {% endfor %}
        </select>

        <label for="dest">To: </label>
        <select id="dest">
            <option value="">Select destination</option>
            {% for place in places %}
            <option value="{{ place }}">{{ place }}</option>
            {% endfor %}
        </select>

        <button id="find-route-btn">Find Route</button>
    </div>

    <div id="map-container">
        <canvas id="campusMap" width="700" height="600"></canvas>
    </div>

    <div id="info">
        <div id="route-text">Click a node to see its image.</div>
        <img id="node-image" src="" alt="" style="display:none;"/>
    </div>

    <script>
        const places = {{ places|tojson }};
        const positions = {{ positions|tojson }};
        const connections = {{ connections|tojson }};
        const images = {{ images|tojson }};

        const canvas = document.getElementById("campusMap");
        const ctx = canvas.getContext("2d");

        // Draw map lines
        function drawConnections() {
            ctx.strokeStyle = "#ccc";
            ctx.lineWidth = 2;
            for (const place in connections) {
                const [x1, y1] = positions[place];
                connections[place].forEach(neighbor => {
                    const [x2, y2] = positions[neighbor];
                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    ctx.stroke();
                });
            }
        }

        // Draw nodes
        function drawNodes() {
            for (const place of places) {
                const [x, y] = positions[place];
                ctx.beginPath();
                ctx.arc(x, y, 12, 0, 2 * Math.PI);
                ctx.fillStyle = "red";
                ctx.fill();
                ctx.strokeStyle = "black";
                ctx.lineWidth = 1;
                ctx.stroke();

                ctx.fillStyle = "black";
                ctx.font = "bold 12px Arial";
                ctx.textAlign = "center";
                ctx.fillText(place, x, y - 18);
            }
        }

        // Clear and redraw map
        function drawMap() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawConnections();
            drawNodes();
        }

        // Utility: Distance between two points
        function dist(x1, y1, x2, y2) {
            return Math.hypot(x2 - x1, y2 - y1);
        }

        // Dijkstra's algorithm
        function dijkstra(start, end) {
            const graph = {};
            for (const place of places) graph[place] = [];

            for (const place in connections) {
                for (const neighbor of connections[place]) {
                    const [x1, y1] = positions[place];
                    const [x2, y2] = positions[neighbor];
                    const distance = dist(x1, y1, x2, y2);
                    graph[place].push({node: neighbor, weight: distance});
                }
            }

            const queue = [{node: start, dist: 0, path: []}];
            const visited = new Set();

            while(queue.length > 0) {
                queue.sort((a,b) => a.dist - b.dist);
                const current = queue.shift();
                if (visited.has(current.node)) continue;
                visited.add(current.node);
                const path = [...current.path, current.node];
                if(current.node === end) {
                    return {distance: current.dist, path};
                }
                for (const neighbor of graph[current.node]) {
                    if(!visited.has(neighbor.node)) {
                        queue.push({node: neighbor.node, dist: current.dist + neighbor.weight, path});
                    }
                }
            }
            return {distance: Infinity, path: []};
        }

        // Highlight route lines
        function highlightRoute(path) {
            if(path.length < 2) return;
            ctx.strokeStyle = "blue";
            ctx.lineWidth = 5;
            for(let i=0; i < path.length -1; i++) {
                const [x1, y1] = positions[path[i]];
                const [x2, y2] = positions[path[i+1]];
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            }
        }

        // Event: Click on canvas to detect node and show image
        canvas.addEventListener("click", (e) => {
            const rect = canvas.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;

            for (const place of places) {
                const [x, y] = positions[place];
                if (dist(clickX, clickY, x, y) <= 12) {
                    showNodeInfo(place);
                    return;
                }
            }
        });

        function showNodeInfo(place) {
            const imgEl = document.getElementById("node-image");
            const textEl = document.getElementById("route-text");
            imgEl.src = images[place];
            imgEl.style.display = "block";
            textEl.textContent = place;
        }

        // Find route button
        document.getElementById("find-route-btn").addEventListener("click", () => {
            const src = document.getElementById("source").value;
            const dst = document.getElementById("dest").value;
            const textEl = document.getElementById("route-text");
            const imgEl = document.getElementById("node-image");
            imgEl.style.display = "none";

            if (!src || !dst) {
                alert("Please select both source and destination!");
                return;
            }
            if (src === dst) {
                alert("Source and destination are the same!");
                return;
            }

            drawMap();
            const result = dijkstra(src, dst);
            if(result.distance === Infinity) {
                textEl.textContent = "No path found!";
                return;
            }
            highlightRoute(result.path);

            textEl.innerHTML = `<strong>Shortest Path:</strong> ${result.path.join(" → ")}<br>
                                <strong>Total Distance:</strong> ${Math.round(result.distance)} units<br>
                                <strong>Estimated Time:</strong> ${Math.round(result.distance / 3)} minutes<br>
                                Path calculated using Dijkstra's Algorithm.`;
        });

        // Initial draw
        drawMap();

    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML,
                                  places=places,
                                  positions=positions,
                                  connections=connections,
                                  images=images)

if __name__ == "__main__":
    app.run(debug=True)
