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
    "Gate": ["EEE Block", "Einstein Block", "Main Block"],
    "EEE Block": ["Gate", "MBA & Mechanical Block", "First Year Block"],
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campus Map Navigation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body { 
            font-family: 'Arial', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated background particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }

        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.7; }
            50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
        }

        header { 
            text-align: center; 
            padding: 30px 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            color: white; 
            font-size: 28px; 
            font-weight: bold; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            animation: slideDown 0.8s ease-out;
        }

        @keyframes slideDown {
            from { transform: translateY(-100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        #map-container { 
            display: flex; 
            justify-content: center; 
            margin: 30px 0;
            animation: fadeInScale 1s ease-out 0.3s both;
        }

        @keyframes fadeInScale {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        canvas { 
            border: none;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        canvas:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }

        #info {
            margin: 20px auto; 
            width: 90vw; 
            max-width: 700px; 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            padding: 25px; 
            border-radius: 15px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            animation: slideUp 0.8s ease-out 0.5s both;
        }

        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        #node-image {
            max-width: 100%; 
            height: auto; 
            margin-top: 20px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            transition: all 0.4s ease;
            transform: scale(0.95);
        }

        #node-image.show {
            transform: scale(1);
            animation: imageReveal 0.6s ease-out;
        }

        @keyframes imageReveal {
            0% { transform: scale(0.8) rotateY(90deg); opacity: 0; }
            50% { transform: scale(1.05) rotateY(45deg); opacity: 0.7; }
            100% { transform: scale(1) rotateY(0deg); opacity: 1; }
        }

        #select-container {
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            margin: 20px auto;
            width: 90%;
            max-width: 800px;
            animation: slideIn 0.8s ease-out 0.2s both;
        }

        @keyframes slideIn {
            from { transform: translateX(-100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        select {
            font-size: 16px;
            padding: 12px 20px;
            margin: 10px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            outline: none;
        }

        select:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }

        select:focus {
            transform: scale(1.05);
            box-shadow: 0 0 0 3px rgba(103, 126, 234, 0.3);
        }

        button {
            font-size: 16px;
            padding: 12px 30px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            border: none;
            color: white;
            border-radius: 25px;
            cursor: pointer;
            margin: 10px;
            box-shadow: 0 5px 15px rgba(238, 90, 82, 0.3);
            transition: all 0.3s ease;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }

        button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s ease;
        }

        button:hover::before {
            left: 100%;
        }

        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(238, 90, 82, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        label {
            color: white;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            margin: 0 10px;
        }

        #route-text {
            font-size: 16px;
            line-height: 1.6;
            color: #333;
            transition: all 0.3s ease;
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .glow {
            box-shadow: 0 0 20px rgba(103, 126, 234, 0.6);
        }

        /* Loading animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(103, 126, 234, 0.3);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Mobile responsiveness */
        @media (max-width: 768px) {
            header { font-size: 22px; padding: 20px 15px; }
            canvas { width: 90vw; height: auto; }
            #select-container { width: 95%; padding: 15px; }
            select, button { margin: 5px; padding: 10px 15px; font-size: 14px; }
        }
    </style>
</head>
<body>
    <!-- Animated background particles -->
    <div class="particles" id="particles"></div>

    <header>AVS ENGINEERING COLLEGE MAP NAVIGATION</header>

    <div id="select-container">
        <label for="source">📍 From: </label>
        <select id="source">
            <option value="">Select source</option>
            {% for place in places %}
            <option value="{{ place }}">{{ place }}</option>
            {% endfor %}
        </select>

        <label for="dest">🎯 To: </label>
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
        <div id="route-text">🖱️ Click a node to see its image, or select locations to find the best route!</div>
        <img id="node-image" src="" alt="" style="display:none;"/>
    </div>

    <script>
        const places = {{ places|tojson }};
        const positions = {{ positions|tojson }};
        const connections = {{ connections|tojson }};
        const images = {{ images|tojson }};

        const canvas = document.getElementById("campusMap");
        const ctx = canvas.getContext("2d");

        // Create animated background particles
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            for (let i = 0; i < 30; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 6 + 's';
                particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
                particlesContainer.appendChild(particle);
            }
        }

        // Animation variables
        let animationProgress = 0;
        let isAnimating = false;
        let hoveredNode = null;
        let pulseRadius = 12;
        let pulseDirection = 1;

        // Enhanced draw connections with gradient
        function drawConnections() {
            for (const place in connections) {
                const [x1, y1] = positions[place];
                connections[place].forEach(neighbor => {
                    const [x2, y2] = positions[neighbor];

                    const gradient = ctx.createLinearGradient(x1, y1, x2, y2);
                    gradient.addColorStop(0, 'rgba(103, 126, 234, 0.3)');
                    gradient.addColorStop(0.5, 'rgba(118, 75, 162, 0.4)');
                    gradient.addColorStop(1, 'rgba(103, 126, 234, 0.3)');

                    ctx.strokeStyle = gradient;
                    ctx.lineWidth = 2;
                    ctx.lineCap = 'round';
                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    ctx.stroke();
                });
            }
        }

        // Enhanced draw nodes with glow effect
        function drawNodes() {
            // Update pulse effect
            pulseRadius += pulseDirection * 0.5;
            if (pulseRadius >= 18 || pulseRadius <= 12) pulseDirection *= -1;

            for (const place of places) {
                const [x, y] = positions[place];
                const isHovered = hoveredNode === place;

                // Glow effect for hovered node
                if (isHovered) {
                    const glowGradient = ctx.createRadialGradient(x, y, 0, x, y, 25);
                    glowGradient.addColorStop(0, 'rgba(255, 107, 107, 0.8)');
                    glowGradient.addColorStop(1, 'rgba(255, 107, 107, 0)');
                    ctx.fillStyle = glowGradient;
                    ctx.fillRect(x - 25, y - 25, 50, 50);
                }

                // Node shadow
                ctx.beginPath();
                ctx.arc(x + 2, y + 2, 12, 0, 2 * Math.PI);
                ctx.fillStyle = "rgba(0, 0, 0, 0.2)";
                ctx.fill();

                // Main node
                ctx.beginPath();
                ctx.arc(x, y, isHovered ? pulseRadius : 12, 0, 2 * Math.PI);

                const nodeGradient = ctx.createRadialGradient(x, y, 0, x, y, 12);
                nodeGradient.addColorStop(0, isHovered ? '#ff6b6b' : '#ff8a80');
                nodeGradient.addColorStop(1, isHovered ? '#ee5a52' : '#ff5722');

                ctx.fillStyle = nodeGradient;
                ctx.fill();
                ctx.strokeStyle = "white";
                ctx.lineWidth = 2;
                ctx.stroke();

                // Node label with shadow
                ctx.fillStyle = "rgba(0, 0, 0, 0.3)";
                ctx.font = "bold 12px Arial";
                ctx.textAlign = "center";
                ctx.fillText(place, x + 1, y - 17);

                ctx.fillStyle = isHovered ? "#ff6b6b" : "#333";
                ctx.fillText(place, x, y - 18);
            }
        }

        // Clear and redraw map with animation
        function drawMap() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Background gradient
            const bgGradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
            bgGradient.addColorStop(0, 'rgba(255, 255, 255, 0.1)');
            bgGradient.addColorStop(1, 'rgba(240, 240, 250, 0.1)');
            ctx.fillStyle = bgGradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            drawConnections();
            drawNodes();
        }

        // Animation loop
        function animate() {
            drawMap();
            requestAnimationFrame(animate);
        }

        // Utility: Distance between two points
        function dist(x1, y1, x2, y2) {
            return Math.hypot(x2 - x1, y2 - y1);
        }

        // Enhanced Dijkstra's algorithm with animation preparation
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

        // Animated route highlighting
        function animateRoute(path) {
            if(path.length < 2) return;

            let segmentIndex = 0;
            let progress = 0;
            const speed = 0.02;

            function drawSegment() {
                if (segmentIndex >= path.length - 1) return;

                const [x1, y1] = positions[path[segmentIndex]];
                const [x2, y2] = positions[path[segmentIndex + 1]];

                const currentX = x1 + (x2 - x1) * progress;
                const currentY = y1 + (y2 - y1) * progress;

                // Animated route line
                const routeGradient = ctx.createLinearGradient(x1, y1, currentX, currentY);
                routeGradient.addColorStop(0, '#667eea');
                routeGradient.addColorStop(1, '#764ba2');

                ctx.strokeStyle = routeGradient;
                ctx.lineWidth = 6;
                ctx.lineCap = 'round';
                ctx.shadowColor = 'rgba(102, 126, 234, 0.5)';
                ctx.shadowBlur = 10;
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(currentX, currentY);
                ctx.stroke();
                ctx.shadowBlur = 0;

                progress += speed;

                if (progress >= 1) {
                    progress = 0;
                    segmentIndex++;
                }

                if (segmentIndex < path.length - 1) {
                    requestAnimationFrame(drawSegment);
                } else {
                    // Route complete - add pulsing effect to destination
                    const [endX, endY] = positions[path[path.length - 1]];
                    let pulseSize = 15;
                    let pulseGrow = true;

                    function pulseDest() {
                        ctx.beginPath();
                        ctx.arc(endX, endY, pulseSize, 0, 2 * Math.PI);
                        ctx.strokeStyle = 'rgba(102, 126, 234, 0.6)';
                        ctx.lineWidth = 3;
                        ctx.stroke();

                        pulseSize += pulseGrow ? 1 : -1;
                        if (pulseSize >= 25 || pulseSize <= 15) pulseGrow = !pulseGrow;

                        setTimeout(pulseDest, 50);
                    }
                    pulseDest();
                }
            }

            drawSegment();
        }

        // Enhanced mouse events
        canvas.addEventListener("mousemove", (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            let foundHover = null;
            for (const place of places) {
                const [x, y] = positions[place];
                if (dist(mouseX, mouseY, x, y) <= 15) {
                    foundHover = place;
                    canvas.style.cursor = 'pointer';
                    break;
                }
            }

            if (!foundHover) {
                canvas.style.cursor = 'default';
            }

            hoveredNode = foundHover;
        });

        canvas.addEventListener("click", (e) => {
            const rect = canvas.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;

            for (con