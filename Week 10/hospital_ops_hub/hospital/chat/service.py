"""Chatbot service: routes a message to the multi-agent graph (scenario), the Q&A agent (question)
or the completion handler (work done for a request id)."""
import re

from langchain.agents import create_agent

from ..graph.builder import build_graph
from ..llm import get_llm, llm_available
from ..models import ChatIntent
from ..operations.completion import complete_requests, queued_requests
from ..reporting.shift_log import get_shift_log
from ..tools import READ_ONLY_TOOLS
from .parser import parse_chat_message, unique_ids

QA_PROMPT = """You are the hospital operations assistant. Answer questions about the CURRENT state of
patients, doctors, beds and staff using the read-only tools. Be concise and use ids (P001, D01, B03, PT01).
If the user describes a new situation that needs action, tell them to send it as a scenario."""

ROUTER_PROMPT = """Classify the hospital operations message:
- completion: the user says work for one or more request ids is done / completed / finished / resolved
  (e.g. "R03 done", "cleaning for R06 is completed", "R02 and R04 finished"). Extract the request ids.
- question: asking about the current state of patients, doctors, beds or staff.
- scenario: something happened or is needed and must be acted on."""

QUESTION_START = re.compile(r"^(how|what|which|who|where|when|is|are|do|does|can|list|show|any)\b", re.I)
REQUEST_ID = re.compile(r"\b([A-Z]{1,3}\d+(?:-[A-Za-z0-9]+)?)\b", re.I)
DONE_WORDS = re.compile(r"\b(done|complete|completed|finished|resolved|over|cleared)\b", re.I)


class HospitalChatService:
    def __init__(self):
        self.graph = build_graph()
        self._qa_agent = None

    def classify_intent(self, text):
        """Return a ChatIntent (intent + any request ids)."""
        if llm_available():
            try:
                router = get_llm().with_structured_output(ChatIntent, method="function_calling")
                result = router.invoke([("system", ROUTER_PROMPT), ("human", text)])
                if result.intent != "completion" or result.request_ids:
                    return result
            except Exception:
                pass
        ids = [i.upper() for i in REQUEST_ID.findall(text) if not i.upper().startswith(("P0", "D0", "B0"))]
        if ids and DONE_WORDS.search(text):
            return ChatIntent(intent="completion", request_ids=ids)
        if text.strip().endswith("?") or QUESTION_START.match(text):
            return ChatIntent(intent="question")
        return ChatIntent(intent="scenario")

    def answer_question(self, text):
        if not llm_available():
            return "Questions need an OPENAI_API_KEY. Check the Shift Report tab for the live tables."
        if self._qa_agent is None:
            self._qa_agent = create_agent(get_llm(), tools=READ_ONLY_TOOLS, system_prompt=QA_PROMPT)
        result = self._qa_agent.invoke({"messages": [{"role": "user", "content": text}]})
        return result["messages"][-1].content

    def run_requests(self, rows):
        """Run a batch (any size, including empty) through the graph and return the final state."""
        rows = unique_ids([dict(r) for r in rows], get_shift_log().existing_request_ids())
        state = self.graph.invoke({"raw_requests": rows}, config={"recursion_limit": 50})
        log = get_shift_log()
        for row in state.get("log_rows", []):
            if row.get("retry_of"):
                log.update_request(row["retry_of"], status="retried",
                                   reason=f"re-run as {row['request_id']} -> {row['status']}")
        return state

    def run_scenario_text(self, text, clock, next_index):
        rows = parse_chat_message(text, clock, next_index)
        return rows, self.run_requests(rows)

    def retry_queued(self, clock):
        """Re-run every queued request at the current clock. Returns (rows, state) or (rows, None)."""
        stamp = clock.isoformat(timespec="minutes")
        rows = [{"request_id": f"{r['request_id'].split('-retry')[0]}-retry", "timestamp": stamp,
                 "description": r["description"], "location": "", "reported_by": "queue",
                 "retry_of": r["request_id"]} for r in queued_requests()]
        return rows, (self.run_requests(rows) if rows else None)

    def complete(self, request_ids, clock):
        """Mark requests done, release their resources, then retry anything queued."""
        results = complete_requests(request_ids, clock.isoformat(timespec="minutes"))
        released_any = any(r.get("released") for r in results)
        rows, retry_state = self.retry_queued(clock) if released_any else ([], None)
        return results, rows, retry_state
