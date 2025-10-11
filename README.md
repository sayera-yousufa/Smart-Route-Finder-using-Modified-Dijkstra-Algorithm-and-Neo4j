#  Smart Path Finder – Optimised Navigation

### Project Overview
**Smart Path Finder** is a unified navigation platform designed to provide efficient, accessible, and personalized pathfinding across **university campuses** and **regional areas (cities)**.  
It ensures smooth navigation for **students, visitors, and physically challenged individuals** by considering accessibility and crowd levels while suggesting routes.

---

## Problem Statement
Large campuses can be confusing to navigate, especially for new students or people with disabilities.  
Similarly, existing city navigation apps lack personalization and accessibility options.  
To address this, we developed **Smart Path Finder**, a platform that:
- Integrates campus and regional navigation,
- Provides **personalized and crowd-aware routing**,
- Supports **multiple languages** and **accessibility preferences**.

---

## Features
- **Campus & Regional Navigation:** Switch easily between two modes.
- **Modified Dijkstra’s Algorithm:** Computes optimized routes considering distance, accessibility, and crowd density.
- **Interactive Map:** Visualizes routes using Leaflet.js.
- **Theme Toggle:** Switch between light and dark modes.
- **Feedback Form:** Collects user opinions and suggestions.
- **Multi-Language Support:** Makes navigation user-friendly for all.
- **Secure Data Handling:** Manages Neo4j AuraDB credentials safely.

---

## Architecture
```

User Input → Dashboard → [Campus: Flask | Regional: Neo4j] → Pathfinding Algorithm → Map Visualization

```

- **Frontend:** HTML, Tailwind CSS, JavaScript, Leaflet.js  
- **Backend:** Flask (Campus), Neo4j (Regional)  
- **Data:** OpenStreetMap, Neo4j AuraDB, CSV files  
- **Data Tools:** Jupyter Notebook, Pandas, OSMNx  
- **Algorithms:**  
  - Modified Dijkstra’s Algorithm (Campus)  
  - Neo4j APOC Dijkstra Procedure (Regional)

---

## License

This project is developed for educational purposes under the **CSE IDDMP Department**.

---

## Acknowledgements

Special thanks to our professors and mentors for their constant guidance and support throughout the project.



