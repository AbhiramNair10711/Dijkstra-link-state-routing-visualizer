# Dijkstra & Link-State Routing Visualizer

A Computer Networks mini-project demonstrating **Link-State Routing** and **Dijkstra's Shortest Path First (SPF)** algorithm through an interactive web interface.

## Features

### Basic
- Add routers
- Add links
- Assign link costs
- Display network topology
- Select source and destination routers
- Run Dijkstra's algorithm
- Generate a routing table
- Show shortest path
- Show total cost

### Additional
- Remove routers and links
- Reset network
- Generate random connected networks
- Highlight shortest path
- Show visited/unvisited routers
- Show tentative distance values
- Show distance updates
- Step-by-step Dijkstra execution
- Smooth in-graph Dijkstra animation

### Failure Simulation

The project demonstrates how routing changes after a link failure:

```text
Normal Network
      |
      v
A link fails
      |
      v
Link-State Database changes
      |
      v
Run Dijkstra again
      |
      v
New shortest paths
      |
      v
New Routing Table
```

A failed link is displayed on the graph and is excluded from the active graph used by Dijkstra.

## Visualization

The graph starts with a **dull topology**. As Dijkstra progresses:

1. The current router is highlighted.
2. Visited routers remain highlighted.
3. Relaxed links are highlighted.
4. Tentative distances are shown as `d=...`.
5. The final shortest path is highlighted.
6. The complete routing table is displayed.

Example path:

```text
A → C → B → D
```

Example routing table:

| Destination | Next Hop | Cost | Path |
|---|---|---:|---|
| A | - | 0 | A |
| B | C | 3 | A → C → B |
| C | C | 2 | A → C |
| D | C | 8 | A → C → B → D |

## Dijkstra Algorithm

The implementation maintains:

- **Distance** — current shortest known distance from the source.
- **Previous** — previous router used to reach each router.
- **Visited** — routers whose shortest distance is finalized.

The process is:

```text
1. Set source distance to 0.
2. Set all other distances to infinity.
3. Select the unvisited router with the smallest distance.
4. Check its neighbouring routers.
5. Calculate a new distance through the current router.
6. If it is smaller, update distance and previous.
7. Mark the current router as visited.
8. Repeat.
```

## Link-State Concept

The routers, active links and their costs form the simplified **Link-State Database (LSDB)**.

For example:

```text
A --4-- B
|       |
2       5
|       |
C --8-- D
```

The link costs are used by Dijkstra to calculate shortest routes.

When a link fails, it is removed from the active graph and the routes are recalculated.

## Project Structure

```text
dijkstra-link-state-simple/
|
|-- app.py
|-- dijkstra.py
|-- network.py
|-- visualization.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|
|-- tests/
|   |-- __init__.py
|   |-- test_dijkstra.py
```

### File Responsibilities

**app.py**
- Streamlit UI
- Controls
- Source/destination selection
- Animation controls
- Routing table
- Failure simulation

**dijkstra.py**
- Dijkstra algorithm
- Distance calculation
- Previous-router tracking
- Path reconstruction
- Routing table generation

**network.py**
- Router and link management
- Link costs
- Random network generation
- Link failure and restoration

**visualization.py**
- Network graph
- Node/link states
- Dijkstra animation
- Shortest-path highlighting

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Enter the project folder:

```bash
cd dijkstra-link-state-simple
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Start Streamlit:

```bash
python -m streamlit run app.py
```

Open the local URL shown in the terminal, normally:

```text
http://localhost:8501
```

## Testing

```bash
pytest -q
```

## Suggested Demonstration

1. Click **Load Demo Network**.
2. Select source **A**.
3. Select destination **D**.
4. Prepare the Dijkstra animation.
5. Play the animation.
6. Observe current, visited and unvisited routers.
7. Observe distance updates.
8. Observe the final shortest path.
9. Check the complete routing table.
10. Simulate a link failure.
11. Run Dijkstra again.
12. Compare the new route and routing table.

## Team Members

| Name | Roll Number | Contribution |
|---|---|---|
| Member 1 | XXXXX | Network, routers, links and failure simulation |
| Member 2 | XXXXX | Dijkstra algorithm and routing table |
| Member 3 | XXXXX | Streamlit UI, graph visualization and animation |

**Replace the placeholders with your actual team details.**

## Technologies Used

- Python
- Streamlit
- NetworkX
- Plotly
- Pytest

## Academic Topic

**Computer Networks — Unit 4: Network Layer**

### Topic
**Dijkstra and Link-State Routing Visualizer**

This project demonstrates how link-state routing uses topology information and Dijkstra's algorithm to calculate shortest paths and construct a routing table.
