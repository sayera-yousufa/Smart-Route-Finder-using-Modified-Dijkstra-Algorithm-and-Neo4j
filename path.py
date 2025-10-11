import pandas as pd
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


# Load CSV files
edges_df = pd.read_csv("edges_all col.csv")
nodes_df = pd.read_csv("nodes_final.csv")

# Convert location names to lowercase
name_to_id = dict(zip(nodes_df['name'].str.lower(), nodes_df['node_id']))
id_to_name = dict(zip(nodes_df['node_id'], nodes_df['name']))

# ========== USER INPUT ==========
source_name = input("Enter source location name: ").strip().lower()
target_name = input("Enter target location name: ").strip().lower()
pref_accessibility = input("Do you want accessibility to be True or False? ").strip().lower()
crowd_pref = input("Do you prefer minimum or maximum crowd level? (min/max): ").strip().lower()

# ========== WEIGHT FUNCTION ==========
def accessibility_penalty(actual, preferred):
    return 0 if str(actual).lower() == preferred else 100

def calculate_weight(distance, accessibility_val, crowd_val, preferred_access, crowd_pref):
    a_penalty = accessibility_penalty(accessibility_val, preferred_access)
    if crowd_pref == 'min':
        crowd_penalty = crowd_val ** 1.5
    else:
        crowd_penalty = (5 - crowd_val) ** 1.5
    return distance + a_penalty + crowd_penalty

# ========== GRAPH BUILDING ==========
graph = {}
edge_info = {}
for _, row in edges_df.iterrows():
    from_node = row['from_node']
    to_node = row['to_node']
    distance = row['distance_m']
    accessibility = row['accessibility']
    crowd = row['crowd_level']
    total_weight = calculate_weight(distance, accessibility, crowd, pref_accessibility, crowd_pref)

    if from_node not in graph:
        graph[from_node] = []
    graph[from_node].append((to_node, total_weight))
    edge_info[(from_node, to_node)] = (accessibility, crowd, distance)

# ========== DIJKSTRA ==========
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

# ========== PATH RECONSTRUCTION ==========
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

# ========== RUN & DISPLAY ==========
if source_name in name_to_id and target_name in name_to_id:
    source_id = name_to_id[source_name]
    target_id = name_to_id[target_name]

    distances, prev_nodes = dijkstra(graph, source_id)
    final_path = reconstruct_path(prev_nodes, source_id, target_id)

    if final_path:
        print("\n🔗 Optimal Path:")
        readable_path = [id_to_name.get(node, f"Node {node}") for node in final_path]
        print(" → ".join(readable_path))
        print(f"📏 Total Weighted Cost: {distances[target_id]:.2f}\n")

        print("🧭 Path Details:")
        for i in range(len(final_path) - 1):
            u, v = final_path[i], final_path[i+1]
            accessibility, crowd, dist = edge_info[(u, v)]
            print(f"  {id_to_name[u]} → {id_to_name[v]}:")
            print(f"     ↳ Distance: {dist} m")
            print(f"     ↳ Accessibility: {accessibility}")
            print(f"     ↳ Crowd Level: {crowd}\n")
    else:
        print("🚫 No path exists based on your preferences.")
        final_path = []
else:
    print("❌ Invalid source or target location name.")
    final_path = []

# ========== VISUALIZATION ==========
G = nx.DiGraph()

# Add nodes with labels
for _, row in nodes_df.iterrows():
    G.add_node(row['node_id'], label=row['name'])

# Add edges
for _, row in edges_df.iterrows():
    G.add_edge(row['from_node'], row['to_node'],
               weight=row['distance_m'],
               accessibility=row['accessibility'],
               crowd=row['crowd_level'])

# Generate layout
pos = nx.spring_layout(G)
def spread_positions(pos, min_dist=0.1):
    for key1, p1 in pos.items():
        for key2, p2 in pos.items():
            if key1 != key2 and np.linalg.norm(np.array(p1) - np.array(p2)) < min_dist:
                pos[key2] = (p2[0] + np.random.uniform(-0.1, 0.1),
                             p2[1] + np.random.uniform(-0.1, 0.1))
    return pos

pos = nx.kamada_kawai_layout(G)
pos = spread_positions(pos)
# Node coloring
node_colors = []
for node in G.nodes():
    if final_path and node == final_path[0]:
        node_colors.append("green")
    elif final_path and node == final_path[-1]:
        node_colors.append("red")
    elif final_path and node in final_path:
        node_colors.append("skyblue")
    else:
        node_colors.append("lightgray")

# Highlight path edges
path_edges = list(zip(final_path, final_path[1:])) if final_path else []
edge_colors = ['orange' if (u, v) in path_edges else 'gray' for u, v in G.edges()]


# Build subgraph with only the nodes in the path
path_set = set(path)
G_path = G.subgraph(path_set).copy()

# Draw only the optimal path
pos = nx.kamada_kawai_layout(G_path)  # or shell_layout, etc.

plt.figure(figsize=(12, 8))
nx.draw(G_path, pos, with_labels=True, node_color='skyblue', node_size=800, font_size=8)

# Highlight path edges
edge_path = list(zip(path[:-1], path[1:]))
nx.draw_networkx_edges(G_path, pos, edgelist=edge_path, edge_color='red', width=2)

plt.title("Optimal Path")
plt.axis('off')
plt.tight_layout()
plt.show()

