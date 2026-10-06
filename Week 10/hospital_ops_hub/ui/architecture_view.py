"""Architecture tab: the LangGraph wiring and what spawns when."""
import streamlit as st

from hospital.orchestrator.playbook import PLAYBOOK

DOT = """
digraph G {
  rankdir=LR; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11];
  START [shape=circle, label="", width=0.2, fillcolor=black];
  orchestrator [label="Manager / Orchestrator\\n(triage + priority sort)", fillcolor="#bfdbfe"];
  patient [label="Patient Agent", fillcolor="#bbf7d0"]; doctor [label="Doctor Agent", fillcolor="#bbf7d0"];
  bed [label="Bed Agent", fillcolor="#bbf7d0"]; staff [label="Staff Agent\\n(clerk / housekeeping /\\nhandling dispatchers)", fillcolor="#bbf7d0"];
  arbiter [label="Resource Arbiter\\n(priority, then timestamp)", fillcolor="#fde68a"];
  realloc [label="Reallocation Worker", fillcolor="#fed7aa"]; gap [label="Staffing Gap Resolver", fillcolor="#fed7aa"];
  esc [label="Escalation Agent", fillcolor="#fecaca"]; synth [label="Synthesizer\\n(log + plan)", fillcolor="#e9d5ff"];
  END [shape=doublecircle, label="", width=0.2, fillcolor=black];
  START -> orchestrator;
  orchestrator -> patient [label="Send()", style=dashed]; orchestrator -> doctor [label="Send()", style=dashed];
  orchestrator -> bed [label="Send()", style=dashed]; orchestrator -> staff [label="Send()", style=dashed];
  patient -> arbiter; doctor -> arbiter; bed -> arbiter; staff -> arbiter;
  arbiter -> realloc [label="Send() if ER & no doctor", style=dashed]; arbiter -> gap [label="Send() if no staff", style=dashed];
  realloc -> arbiter; gap -> arbiter;
  arbiter -> esc [label="Send() if unassigned", style=dashed]; arbiter -> synth; esc -> synth; synth -> END;
}
"""


def render_architecture():
    st.subheader("How a request flows")
    st.graphviz_chart(DOT, width="stretch")
    st.markdown("""
- **Manager / Orchestrator** classifies each request with `gpt-4o-mini` (type + priority), sorts emergencies
  first, resolves or reserves a patient id, and emits one `Send()` per agent the request needs.
  Batch size and mix are never hard-coded.
- **Four resource agents** run in parallel and *propose* ranked candidates using their read tools.
- **Resource Arbiter** commits claims through the write tools in priority → timestamp order, so a doctor,
  bed or porter claimed twice goes to the more urgent / earlier request; losers try their next option.
- **Reallocation Worker**, **Staffing Gap Resolver** and **Escalation Agent** are only spawned when needed.
- **Synthesizer** writes the fixed-schema log row per request and the current plan.
""")
    st.markdown("**Agents spawned per request type**")
    st.table([{"Request type": t, "Send() targets": ", ".join(f"{n} ({task})" for n, task in steps)}
              for t, steps in PLAYBOOK.items()] + [{"Request type": "malformed", "Send() targets": "Escalation Agent"}])
