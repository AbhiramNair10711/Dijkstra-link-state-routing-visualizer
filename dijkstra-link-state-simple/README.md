
# Dijkstra & Link-State Routing Visualizer

A simple, explainable Computer Networks mini-project that demonstrates
Link-State Routing and Dijkstra's Shortest Path First algorithm.

## Main Features

- Add routers
- Add weighted links
- Display network topology
- Select source and destination
- Run Dijkstra
- Generate routing table
- Show shortest path and total cost
- Remove routers and links
- Reset network
- Generate random connected networks
- Show current/visited/unvisited routers
- Show distance updates
- Step-by-step Dijkstra execution
- Animate every Dijkstra step directly on the graph
- Simulate link failure and recalculate routes

## Failure Simulation

The failure feature demonstrates:

```text
Normal Network
      ↓
Router B ↔ C link fails
      ↓
Link-State Database changes
      ↓
Dijkstra runs again
      ↓
New shortest paths
      ↓
New routing table
```

A failed link is shown as a broken/dashed connection.
Dijkstra ignores that link until it is restored.

## Project Structure

```text
dijkstra-link-state-simple/
│
├── app.py
├── dijkstra.py
├── network.py
├── visualization.py
├── tests/
│   └── test_dijkstra.py
├── requirements.txt
├── README.md
└── .gitignore
```

This intentionally uses only a few files so the project is easy to explain
during a viva.

## Run

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Test

```bash
pytest -q
```

## Viva Explanation

### Network

The network is stored as routers and weighted links.

### Dijkstra

The algorithm maintains:

- `distance[]` — current shortest known cost
- `previous[]` — previous router in the shortest path
- `visited[]` — routers whose shortest distance is finalized

For every selected router:

```text
new distance = current distance + link cost
```

If the new distance is smaller, the distance is updated.

### Routing Table

After Dijkstra finishes, the application uses `previous[]`
to reconstruct each path and find the next hop.

### Link-State

The active links and their costs form the simplified Link-State Database.
Dijkstra uses this topology information to calculate routes.

### Failure Simulation

When a link fails, it is marked inactive.
The Link-State Database no longer uses that link for Dijkstra.
Running Dijkstra again produces a new routing table.

## Team Division

### Member 1
- Network builder
- Add/remove routers and links
- Random topology
- Failure simulation

### Member 2
- Dijkstra algorithm
- Distance updates
- Path reconstruction
- Routing table

### Member 3
- Streamlit UI
- Plotly graph visualization
- Animation
- Testing and documentation


## 🎬 Smooth Graph Animation

The animation uses Plotly **frames** instead of repeatedly replacing the
Streamlit graph. This prevents the blinking/laggy effect.

The topology keeps the same node positions for every frame:

```text
Initial:
A -- B
|    |
C -- D
(all links dull)

        ↓

Step 1:
A -- B
|    |
C -- D
A = current

        ↓

Step 2:
A == B
|    |
C -- D
B = current
A = visited

        ↓

Final:
A == B
|    |
C == D
selected shortest path highlighted
```

The slider can also be dragged manually through every Dijkstra iteration.


## Final Output

After Dijkstra is prepared, the complete routing table is displayed:

| Destination | Next Hop | Cost | Path |
|---|---|---:|---|
| A | — | 0 | A |
| B | C | 3 | A → C → B |
| C | C | 2 | A → C |
| D | C | 8 | A → C → B → D |
| E | C | 10 | A → C → B → D → E |

The table is shown independently of the animation. This means the user can
watch the graph animation and still immediately see the complete routing
output. The selected source-to-destination route is also highlighted below
the table with its total cost and next hop.
