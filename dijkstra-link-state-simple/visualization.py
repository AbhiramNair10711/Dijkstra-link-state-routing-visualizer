
import networkx as nx
import plotly.graph_objects as go
from math import inf


# Fixed colors make the algorithm's movement easy to read.
DULL = "#D9DEE7"
ACTIVE = "#2E86DE"
VISITED = "#58B368"
CURRENT = "#F4B942"
SOURCE = "#7B61FF"
DESTINATION = "#E45756"
PATH = "#F39C12"
FAILED = "#E45756"


def _layout(network):
    """Create one fixed layout so nodes never jump between animation frames."""
    graph = nx.Graph()
    graph.add_nodes_from(sorted(network.routers))

    for a, b, cost, failed in network.all_edges():
        graph.add_edge(a, b)

    return nx.spring_layout(graph, seed=10)


def _edge_key(a, b):
    return tuple(sorted((a, b)))


def make_animation_figure(
    network,
    steps,
    source,
    destination,
):
    """
    Build ONE Plotly figure containing all Dijkstra states as animation frames.

    This is smoother than repeatedly replacing a Streamlit chart.
    The graph stays in the same position and only the node/edge state changes.
    """
    graph = nx.Graph()
    graph.add_nodes_from(sorted(network.routers))

    for a, b, cost, failed in network.all_edges():
        graph.add_edge(a, b, cost=cost, failed=failed)

    if not graph.nodes:
        return go.Figure()

    pos = _layout(network)

    all_edges = list(graph.edges())
    edge_cost = {
        _edge_key(a, b): cost
        for a, b, cost, failed in network.all_edges()
    }
    failed_edges = {
        _edge_key(a, b)
        for a, b, cost, failed in network.all_edges()
        if failed
    }

    def edge_state(step, a, b, final=False):
        key = _edge_key(a, b)

        if key in failed_edges:
            return FAILED, 4, "dash"

        if final and key in step["final_edges"]:
            return PATH, 8, "solid"

        if key in {_edge_key(x, y) for x, y in step["relaxed"]}:
            return ACTIVE, 6, "solid"

        # Edges from visited nodes remain softly highlighted.
        visited = step["visited"]
        if a in visited and b in visited:
            return VISITED, 4, "solid"

        return DULL, 2, "solid"

    def node_state(step, node):
        if node == step["current"]:
            return CURRENT, 60
        if node == source:
            return SOURCE, 54
        if node == destination:
            return DESTINATION, 54
        if node in step["visited"]:
            return VISITED, 48
        return DULL, 44

    def make_edge_traces(step, final=False):
        traces = []

        for a, b in all_edges:
            x1, y1 = pos[a]
            x2, y2 = pos[b]

            color, width, dash = edge_state(
                step, a, b, final=final
            )

            traces.append(
                go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode="lines",
                    line=dict(
                        color=color,
                        width=width,
                        dash=dash,
                    ),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

        return traces

    def make_cost_annotations(step):
        annotations = []

        for a, b in all_edges:
            x1, y1 = pos[a]
            x2, y2 = pos[b]

            key = _edge_key(a, b)
            text = (
                "FAILED"
                if key in failed_edges
                else str(edge_cost[key])
            )

            annotations.append(
                dict(
                    x=(x1 + x2) / 2,
                    y=(y1 + y2) / 2,
                    text=text,
                    showarrow=False,
                    bgcolor="white",
                    bordercolor="gray",
                    borderwidth=1,
                    font=dict(size=12),
                )
            )

        return annotations

    def make_node_trace(step):
        x = []
        y = []
        text = []
        colors = []
        sizes = []
        hover = []

        for node in sorted(graph.nodes):
            x0, y0 = pos[node]

            distance = step["distance"].get(node, inf)
            d = "∞" if distance == inf else str(distance)

            color, size = node_state(step, node)

            x.append(x0)
            y.append(y0)
            colors.append(color)
            sizes.append(size)

            # The distance is part of the node itself.
            text.append(f"{node}<br>d={d}")

            state = (
                "CURRENT"
                if node == step["current"]
                else "SOURCE"
                if node == source
                else "DESTINATION"
                if node == destination
                else "VISITED"
                if node in step["visited"]
                else "UNVISITED"
            )

            hover.append(
                f"Router {node}<br>"
                f"State: {state}<br>"
                f"Distance: {d}"
            )

        return go.Scatter(
            x=x,
            y=y,
            mode="markers+text",
            text=text,
            textposition="middle center",
            marker=dict(
                size=sizes,
                color=colors,
                line=dict(color="white", width=2),
            ),
            hovertext=hover,
            hoverinfo="text",
            showlegend=False,
        )

    def frame_data(step, final=False):
        traces = make_edge_traces(step, final=final)
        traces.append(make_node_trace(step))
        return traces

    # First frame = initial dull topology.
    initial = steps[0]
    initial["final_edges"] = []

    base_traces = frame_data(initial, final=False)

    fig = go.Figure(
        data=base_traces,
        layout=go.Layout(
            height=620,
            margin=dict(l=20, r=20, t=80, b=20),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                visible=False,
                range=[
                    min(p[0] for p in pos.values()) - 0.25,
                    max(p[0] for p in pos.values()) + 0.25,
                ],
            ),
            yaxis=dict(
                visible=False,
                range=[
                    min(p[1] for p in pos.values()) - 0.25,
                    max(p[1] for p in pos.values()) + 0.25,
                ],
                scaleanchor="x",
                scaleratio=1,
            ),
            title=dict(
                text="Step 0 — Initial network",
                x=0.02,
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    x=0.02,
                    y=1.10,
                    xanchor="left",
                    yanchor="top",
                    buttons=[
                        dict(
                            label="▶ Play Dijkstra",
                            method="animate",
                            args=[
                                None,
                                dict(
                                    frame=dict(
                                        duration=850,
                                        redraw=True,
                                    ),
                                    transition=dict(
                                        duration=350,
                                    ),
                                    fromcurrent=True,
                                    mode="immediate",
                                ),
                            ],
                        ),
                        dict(
                            label="⏸ Pause",
                            method="animate",
                            args=[
                                [None],
                                dict(
                                    frame=dict(
                                        duration=0,
                                        redraw=False,
                                    ),
                                    mode="immediate",
                                ),
                            ],
                        ),
                    ],
                )
            ],
            sliders=[
                dict(
                    active=0,
                    x=0.20,
                    y=1.08,
                    len=0.72,
                    currentvalue=dict(
                        prefix="Dijkstra step: "
                    ),
                    steps=[],
                )
            ],
        ),
        frames=[],
    )

    frames = []
    slider_steps = []

    # Build each progressive state.
    for index, original_step in enumerate(steps):
        step = dict(original_step)

        final = index == len(steps) - 1

        final_path = []
        if final:
            # The final path is reconstructed by the app before calling us.
            final_path = step.get("final_path", [])

        step["final_edges"] = list(
            zip(final_path[:-1], final_path[1:])
        )

        traces = frame_data(step, final=final)

        if step["current"]:
            title = (
                f"Step {index} — "
                f"Current router: {step['current']} "
                f"| Visited: "
                f"{', '.join(sorted(step['visited'])) or 'None'}"
            )
        else:
            title = "Step 0 — Initialize source"

        frame = go.Frame(
            name=str(index),
            data=traces,
            layout=go.Layout(
                title=dict(text=title),
                annotations=make_cost_annotations(
                    step
                ),
            ),
        )

        frames.append(frame)

        slider_steps.append(
            dict(
                label=str(index),
                method="animate",
                args=[
                    [str(index)],
                    dict(
                        mode="immediate",
                        frame=dict(
                            duration=700,
                            redraw=True,
                        ),
                        transition=dict(
                            duration=300,
                        ),
                    ),
                ],
            )
        )

    fig.frames = frames
    fig.update_layout(
        sliders=[
            dict(
                active=0,
                x=0.20,
                y=1.08,
                len=0.72,
                currentvalue=dict(
                    prefix="Dijkstra step: "
                ),
                steps=slider_steps,
            )
        ]
    )

    return fig


def draw_network(
    network,
    source=None,
    destination=None,
    current=None,
    visited=None,
    relaxed=None,
    final_path=None,
    distances=None
):
    """
    Static graph used before/after animation.
    The same visual language as the animated graph is used.
    """
    visited = visited or set()
    relaxed = relaxed or []
    final_path = final_path or []
    distances = distances or {}

    graph = nx.Graph()
    graph.add_nodes_from(sorted(network.routers))

    for a, b, cost, failed in network.all_edges():
        graph.add_edge(a, b, cost=cost, failed=failed)

    if not graph.nodes:
        return go.Figure()

    pos = _layout(network)

    fig = go.Figure()

    for a, b, data in graph.edges(data=True):
        key = _edge_key(a, b)
        x1, y1 = pos[a]
        x2, y2 = pos[b]

        if data["failed"]:
            color, width, dash = FAILED, 4, "dash"
        elif key in {
            _edge_key(x, y) for x, y in final_path
        }:
            color, width, dash = PATH, 8, "solid"
        elif key in {
            _edge_key(x, y) for x, y in relaxed
        }:
            color, width, dash = ACTIVE, 6, "solid"
        else:
            color, width, dash = DULL, 2, "solid"

        fig.add_trace(go.Scatter(
            x=[x1, x2],
            y=[y1, y2],
            mode="lines",
            line=dict(color=color, width=width, dash=dash),
            hoverinfo="none",
            showlegend=False,
        ))

        fig.add_annotation(
            x=(x1 + x2) / 2,
            y=(y1 + y2) / 2,
            text="FAILED" if data["failed"] else str(data["cost"]),
            showarrow=False,
            bgcolor="white",
            bordercolor="gray",
        )

    x = []
    y = []
    text = []
    colors = []
    sizes = []

    for node in sorted(graph.nodes):
        x0, y0 = pos[node]
        d = distances.get(node, inf)
        d = "∞" if d == inf else str(d)

        if node == current:
            color, size = CURRENT, 60
        elif node == source:
            color, size = SOURCE, 54
        elif node == destination:
            color, size = DESTINATION, 54
        elif node in visited:
            color, size = VISITED, 48
        else:
            color, size = DULL, 44

        x.append(x0)
        y.append(y0)
        text.append(f"{node}<br>d={d}")
        colors.append(color)
        sizes.append(size)

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="markers+text",
        text=text,
        textposition="middle center",
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(color="white", width=2),
        ),
        showlegend=False,
    ))

    fig.update_layout(
        height=620,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="white",
        xaxis=dict(visible=False),
        yaxis=dict(
            visible=False,
            scaleanchor="x",
            scaleratio=1,
        ),
    )

    return fig
