import pandas as pd
import heapq

# Load CSV files
edges_df = pd.read_csv("edges_all col.csv")
nodes_df = pd.read_csv("nodes_final.csv")

# Convert location names to lowercase
name_to_id = dict(zip(nodes_df['name'].str.lower(), nodes_df['node_id']))
id_to_name = dict(zip(nodes_df['node_id'], nodes_df['name']))

# User preferences
source_name = input("Enter source location name: ").strip().lower()
target_name = input("Enter target location name: ").strip().lower()
pref_accessibility = input("Do you want accessibility to be True or False? ").strip().lower()
crowd_pref = input("Do you prefer minimum or maximum crowd level? (min/max): ").strip().lower()

# Convert accessibility to penalty
def accessibility_penalty(actual, preferred):
    return 0 if str(actual).lower() == preferred else 100  # heavy penalty for mismatch

# Complex weight function based on preferences
def calculate_weight(distance, accessibility_val, crowd_val, preferred_access, crowd_pref):
    a_penalty = accessibility_penalty(accessibility_val, preferred_access)
    
    if crowd_pref == 'min':
        crowd_penalty = crowd_val ** 1.5  # more crowd = worse
    else:
        crowd_penalty = (5 - crowd_val) ** 1.5  # less crowd = worse
    
    return distance + a_penalty + crowd_penalty

# Build graph
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

# Dijkstra's Algorithm
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

# Reconstruct path
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

# Validate user input
if source_name in name_to_id and target_name in name_to_id:
    source_id = name_to_id[source_name]
    target_id = name_to_id[target_name]

    distances, prev_nodes = dijkstra(graph, source_id)
    path = reconstruct_path(prev_nodes, source_id, target_id)

    if path:
        readable_path = [id_to_name.get(node, f"Node {node}") for node in path]
        print("\n🔗 Optimal Path:")
        print(" → ".join(readable_path))
        print(f"📏 Total Weighted Cost: {distances[target_id]:.2f}\n")

        print("🧭 Path Details:")
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            accessibility, crowd, dist = edge_info[(u, v)]
            print(f"  {id_to_name[u]} → {id_to_name[v]}:")
            print(f"     ↳ Distance: {dist} m")
            print(f"     ↳ Accessibility: {accessibility}")
            print(f"     ↳ Crowd Level: {crowd}\n")
    else:
        print("🚫 No path exists based on your preferences.")
else:
    print("❌ Invalid source or target location name.")
