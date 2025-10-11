from flask import Flask, request, jsonify
import pandas as pd
import heapq

app = Flask(__name__)

# Load data once
edges_df = pd.read_csv("edges_all col.csv")
nodes_df = pd.read_csv("nodes_final.csv")
name_to_id = dict(zip(nodes_df['name'].str.lower(), nodes_df['node_id']))
id_to_name = dict(zip(nodes_df['node_id'], nodes_df['name']))

def accessibility_penalty(actual, preferred):
    return 0 if str(actual).lower() == preferred else 100

def calculate_weight(distance, accessibility_val, crowd_val, preferred_access, crowd_pref):
    a_penalty = accessibility_penalty(accessibility_val, preferred_access)
    if crowd_pref == 'min':
        crowd_penalty = crowd_val ** 1.5
    else:
        crowd_penalty = (5 - crowd_val) ** 1.5
    return distance + a_penalty + crowd_penalty

def build_graph(pref_accessibility, crowd_pref):
    graph = {}
    edge_info = {}
    for _, row in edges_df.iterrows():
        from_node = row['from_node']
        to_node = row['to_node']
        dist = row['distance_m']
        access = row['accessibility']
        crowd = row['crowd_level']
        weight = calculate_weight(dist, access, crowd, pref_accessibility, crowd_pref)
        graph.setdefault(from_node, []).append((to_node, weight))
        edge_info[(from_node, to_node)] = (access, crowd, dist)
    return graph, edge_info

def dijkstra(graph, start_node):
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0
    prev = {}
    pq = [(0, start_node)]
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        if current_dist > distances[current_node]:
            continue
        for neighbor, weight in graph.get(current_node, []):
            new_dist = current_dist + weight
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                prev[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))
    return distances, prev

def reconstruct_path(prev, start, end):
    path = []
    current = end
    while current != start:
        path.append(current)
        current = prev.get(current)
        if current is None:
            return []
    path.append(start)
    return path[::-1]
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_url_path='', static_folder='static')  # assuming you put index.html in a folder called "static"

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/get_locations')
def get_locations():
    locations = sorted(nodes_df['name'].tolist())
    return jsonify({'locations': locations})

@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.get_json()
    src = data['source'].lower()
    tgt = data['target'].lower()
    pref_access = data['accessibility']
    crowd_pref = data['crowd']

    if src not in name_to_id or tgt not in name_to_id:
        return jsonify({'success': False, 'message': "Invalid location name"})

    source_id = name_to_id[src]
    target_id = name_to_id[tgt]

    graph, edge_info = build_graph(pref_access, crowd_pref)
    distances, prev_nodes = dijkstra(graph, source_id)
    path = reconstruct_path(prev_nodes, source_id, target_id)

    if not path:
        return jsonify({'success': False, 'message': "No path exists based on your preferences."})

    readable_path = [id_to_name.get(node, f"Node {node}") for node in path]
    details = ""
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        access, crowd, dist = edge_info[(u, v)]
        details += f"{id_to_name[u]} → {id_to_name[v]}:\n  ↳ Distance: {dist} m\n  ↳ Accessibility: {access}\n  ↳ Crowd Level: {crowd}\n\n"

    return jsonify({
        'success': True,
        'path': readable_path,
        'total_cost': distances[target_id],
        'details': details
    })
from flask import Flask, send_from_directory

@app.route('/smart_path_map.html')
def map_html():
    return send_from_directory('.', 'smart_path_map.html')  # serve from current directory

if __name__ == '__main__':
    app.run(debug=True, port=5050)
