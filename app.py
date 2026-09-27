
import streamlit as st

from network import Network
from dijkstra import dijkstra, get_path, make_routing_table
from visualization import draw_network, make_animation_figure


st.set_page_config(
    page_title="Dijkstra Link-State Visualizer",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Dijkstra & Link-State Routing Visualizer")
st.caption("Computer Networks • Unit 4 • Network Layer")


# ============================================================
# SESSION STATE
# ============================================================

if "network" not in st.session_state:
    st.session_state.network = Network()

if "steps" not in st.session_state:
    st.session_state.steps = []

if "step_index" not in st.session_state:
    st.session_state.step_index = 0

if "source" not in st.session_state:
    st.session_state.source = None

if "destination" not in st.session_state:
    st.session_state.destination = None


network = st.session_state.network


def reset_dijkstra():
    st.session_state.steps = []
    st.session_state.step_index = 0


# ============================================================
# SIDEBAR - BUILD THE NETWORK
# ============================================================

with st.sidebar:
    st.header("Network Builder")

    # ---------- Add Router ----------
    st.subheader("Add Router")

    router_name = st.text_input(
        "Router name",
        placeholder="A"
    )

    if st.button("Add Router", use_container_width=True):
        name = router_name.strip().upper()

        if not name:
            st.error("Enter a router name.")
        elif name in network.routers:
            st.warning("Router already exists.")
        elif len(name) != 1 or not name.isalpha():
            st.warning("Use one letter: A, B, C...")
        else:
            network.add_router(name)
            reset_dijkstra()
            st.rerun()

    routers = sorted(network.routers)

    # ---------- Add Link ----------
    st.subheader("Add Link")

    if len(routers) >= 2:
        a = st.selectbox("Router A", routers)
        b_options = [r for r in routers if r != a]
        b = st.selectbox("Router B", b_options)

        cost = st.number_input(
            "Link cost",
            min_value=1,
            max_value=100,
            value=1
        )

        if st.button("Add / Update Link", use_container_width=True):
            network.add_link(a, b, cost)
            reset_dijkstra()
            st.rerun()

    # ---------- Remove ----------
    st.subheader("Remove")

    if routers:
        remove_router = st.selectbox(
            "Router to remove",
            routers,
            key="remove_router"
        )

        if st.button("Remove Router", use_container_width=True):
            network.remove_router(remove_router)
            reset_dijkstra()
            st.rerun()

    if network.links:
        link_labels = [
            f"{a} ↔ {b} (cost {cost})"
            for a, b, cost, failed in network.all_edges()
        ]

        selected_link = st.selectbox(
            "Link to remove",
            link_labels
        )

        if st.button("Remove Link", use_container_width=True):
            index = link_labels.index(selected_link)
            a, b, _, _ = network.all_edges()[index]
            network.remove_link(a, b)
            reset_dijkstra()
            st.rerun()

    # ========================================================
    # FAILURE SIMULATION
    # ========================================================

    st.divider()
    st.header("⚠️ Failure Simulation")

    st.write(
        "Simulate a link failure, update the Link-State Database, "
        "and run Dijkstra again."
    )

    active_edges = network.active_edges()

    if active_edges:
        failure_labels = [
            f"{a} ↔ {b} (cost {cost})"
            for a, b, cost in active_edges
        ]

        failure_choice = st.selectbox(
            "Link that fails",
            failure_labels
        )

        if st.button(
            "Simulate Link Failure",
            use_container_width=True
        ):
            index = failure_labels.index(failure_choice)
            a, b, _ = active_edges[index]

            network.fail_link(a, b)
            reset_dijkstra()

            st.success(f"Link {a} ↔ {b} failed.")
            st.rerun()

    if network.failed_links:
        if st.button(
            "Restore Failed Links",
            use_container_width=True
        ):
            for a, b in list(network.failed_links):
                network.restore_link(a, b)

            reset_dijkstra()
            st.rerun()

    # ========================================================
    # RANDOM NETWORK
    # ========================================================

    st.divider()
    st.header("Random Network")

    count = st.slider(
        "Number of routers",
        2,
        10,
        6
    )

    min_cost = st.number_input(
        "Minimum cost",
        1,
        50,
        1,
        key="min_random"
    )

    max_cost = st.number_input(
        "Maximum cost",
        1,
        50,
        10,
        key="max_random"
    )

    if st.button(
        "Generate Random Network",
        use_container_width=True
    ):
        network.random_network(count, min_cost, max_cost)

        routers = sorted(network.routers)
        st.session_state.source = routers[0]
        st.session_state.destination = routers[-1]

        reset_dijkstra()
        st.rerun()

    # ========================================================
    # DEMO / RESET
    # ========================================================

    st.divider()

    if st.button(
        "Load Demo Network",
        use_container_width=True
    ):
        network.demo()

        st.session_state.source = "A"
        st.session_state.destination = "D"

        reset_dijkstra()
        st.rerun()

    if st.button(
        "Reset Network",
        use_container_width=True
    ):
        network.clear()

        st.session_state.source = None
        st.session_state.destination = None

        reset_dijkstra()
        st.rerun()


# ============================================================
# MAIN SCREEN
# ============================================================

if not routers:
    st.info(
        "Add routers from the sidebar, or click "
        "**Load Demo Network**."
    )
    st.stop()


# ============================================================
# SOURCE + DESTINATION
# ============================================================

st.subheader("1. Select Source and Destination")

col1, col2 = st.columns(2)

with col1:
    source = st.selectbox(
        "Source Router",
        routers,
        index=(
            routers.index(st.session_state.source)
            if st.session_state.source in routers
            else 0
        )
    )

st.session_state.source = source

possible_destinations = [
    r for r in routers if r != source
]

with col2:
    destination = st.selectbox(
        "Destination Router",
        possible_destinations,
        index=(
            possible_destinations.index(
                st.session_state.destination
            )
            if st.session_state.destination in possible_destinations
            else 0
        )
    )

st.session_state.destination = destination


# ============================================================
# TOPOLOGY
# ============================================================

st.subheader("2. Network Topology")

graph_area = st.empty()

graph_area.plotly_chart(
    draw_network(
        network,
        source=source,
        destination=destination
    ),
    use_container_width=True,
    key="initial_graph"
)


# ============================================================
# DIJKSTRA CONTROLS
# ============================================================

st.subheader("3. Dijkstra Animation")

st.info(
    "The animation is rendered inside one Plotly graph. "
    "The topology stays fixed while nodes and links progressively "
    "change from dull → visited/current → highlighted."
)

c1, c2 = st.columns(2)

with c1:
    run = st.button(
        "▶ Prepare Dijkstra Animation",
        type="primary",
        use_container_width=True
    )

with c2:
    reset = st.button(
        "↺ Reset Dijkstra",
        use_container_width=True
    )

if reset:
    reset_dijkstra()
    st.rerun()


# ------------------------------------------------------------
# Prepare ONE animation figure.
# No time.sleep(), no repeated Streamlit chart replacement.
# This prevents the blinking/laggy effect.
# ------------------------------------------------------------

if run:
    graph = network.adjacency()

    _, _, steps = dijkstra(
        graph,
        source
    )

    # Add the selected final path to the last frame.
    final_path = get_path(
        steps[-1]["previous"],
        source,
        destination
    )

    steps[-1]["final_path"] = final_path

    st.session_state.steps = steps
    st.session_state.step_index = 0


if st.session_state.steps:

    animation_steps = st.session_state.steps

    # Make sure final frame knows the selected path.
    if "final_path" not in animation_steps[-1]:
        animation_steps[-1]["final_path"] = get_path(
            animation_steps[-1]["previous"],
            source,
            destination
        )

    st.markdown("### Live Dijkstra Graph")

    st.plotly_chart(
        make_animation_figure(
            network,
            animation_steps,
            source,
            destination
        ),
        use_container_width=True,
        key="smooth_dijkstra_animation"
    )

    st.caption(
        "Use ▶ Play Dijkstra for continuous movement or drag the "
        "Dijkstra step slider to inspect each iteration."
    )

    st.markdown(
        "**Visual sequence:** "
        "dull topology → current router → relaxed links → "
        "visited routers → updated distances → final shortest path."
    )

# ============================================================
# LINK-STATE DATABASE

# ============================================================

st.subheader("4. Link-State Database")

if network.all_edges():

    rows = []

    for a, b, cost, failed in network.all_edges():

        rows.append({
            "Router A": a,
            "Router B": b,
            "Cost": cost,
            "Status": "FAILED" if failed else "ACTIVE"
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("No links have been created.")


# ============================================================
# CURRENT DIJKSTRA STATE
# ============================================================

if st.session_state.steps:

    step = st.session_state.steps[
        st.session_state.step_index
    ]

    st.subheader(
        f"5. Dijkstra State "
        f"(Step {st.session_state.step_index + 1}/"
        f"{len(st.session_state.steps)})"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            "**Current Router:**",
            step["current"] or "Initialization"
        )

        st.write(
            "**Visited:**",
            ", ".join(sorted(step["visited"]))
            or "None"
        )

    with col2:
        st.write(
            "**Action:**",
            step["message"]
        )

    # Distance table.
    distance_rows = []

    for router in routers:

        distance = step["distance"][router]

        if distance == float("inf"):
            display_distance = "∞"
        else:
            display_distance = distance

        if router == step["current"]:
            state = "CURRENT"
        elif router in step["visited"]:
            state = "VISITED"
        else:
            state = "UNVISITED"

        distance_rows.append({
            "Router": router,
            "Distance": display_distance,
            "Previous": step["previous"][router] or "-",
            "State": state
        })

    st.write("**Distance Updates / Visited State**")

    st.dataframe(
        distance_rows,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FINAL ROUTING TABLE
# ============================================================

# As soon as Dijkstra has been prepared, show the complete result.
# The animation is only the visual explanation of the algorithm;
# the routing table is the actual final output.
if st.session_state.steps:

    final = st.session_state.steps[-1]

    st.subheader("6. Final Routing Table")

    table = make_routing_table(
        network.adjacency(),
        source,
        final["distance"],
        final["previous"]
    )

    # This is the complete output requested for the project:
    # Destination | Next Hop | Cost | Path
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )

    selected_row = next(
        row
        for row in table
        if row["Destination"] == destination
    )

    st.success(
        f"**Shortest Path:** {selected_row['Path']}  \n"
        f"**Total Cost:** {selected_row['Cost']}  \n"
        f"**Next Hop:** {selected_row['Next Hop']}"
    )

    st.caption(
        "The Path column shows the complete route using arrows, "
        "for example: A → C → B → D."
    )

# ============================================================
# FAILURE EXPLANATION
# ============================================================

if network.failed_links:

    st.warning(
        "A link failure is currently active. "
        "The failed link is removed from the Link-State Database "
        "used by Dijkstra. Run Dijkstra again to calculate the "
        "new routes."
    )

st.divider()

st.markdown(
    "**Legend:** Current = router being processed • "
    "Visited = shortest distance finalized • "
    "`d=` = current tentative distance • "
    "Failed link = broken connection • "
    "Final highlighted path = shortest route."
)
