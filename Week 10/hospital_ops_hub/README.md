# 🏥 Hospital Operations Hub — multi-agent chatbot

LangGraph + OpenAI (`gpt-4o-mini`) + Streamlit. A **manager (orchestrator)** triages each scenario and
spawns the **Patient, Doctor, Bed and Staff agents** on demand with `Send()`. Control agents settle
conflicts, cover shortages, escalate what can't be solved, and write a shift report.

## Run

```bash
cd "Week 10/hospital_ops_hub"
pip install -r requirements.txt          # already satisfied in this repo's environment
# put OPENAI_API_KEY in a .env here or in any parent folder (see .env.example)
streamlit run app.py
```

## Using the chatbot

| You type | What happens |
|---|---|
| A scenario, e.g. *"Young woman unconscious with seizures, needs neurologist now"* | Full multi-agent run; the reply is the **current plan** with per-request cards, the agents that were spawned, conflicts, and escalations |
| Several scenarios, one per line | Treated as one batch, with emergencies handled first |
| Rows pasted from a request CSV (`R02,2026-10-02T08:08,"Ambulance..."`) | Uses their own ids and timestamps |
| A question, e.g. *"Which beds are free?"* | A read-only Q&A agent answers from the live lists |
| Finished work, e.g. *"R02 is done"*, *"R03 and R06 completed"* | Releases that request's staff, puts an ER doctor back to available (if their caseload allows), marks the row `completed`, then automatically retries every **queued** request |

**Queued** means routine work is waiting for a resource (doctor, porter, bed) that is busy right now.
Resources are released only when you report the work as done, so completing a request is what moves the queue.

Sidebar: simulation clock (chat scenarios are timestamped with it), one-click test batches
(`requests_5`, `requests_12`, `requests_empty`, `requests_shortage`), CSV upload, retry queued items,
and reset to seed data.

**Current shift report tab:** live CSVs of patients, doctors, beds, staff, the request log
(fixed schema), the agent trace and escalations. Each one can be downloaded, or download them all as a zip.
**End shift** archives everything to `reports/shift_XXX_<time>/` and starts a new shift log.
The resources carry over to the new shift.

## Architecture

```
START → orchestrator ──Send()──► patient_agent ┐
                     ──Send()──► doctor_agent  ├─► arbiter ──Send() if ER & no doctor──► reallocation_worker ─┐
                     ──Send()──► bed_agent     │           ──Send() if no staff─────────► staffing_gap_resolver ┤
                     ──Send()──► staff_agent   ┘           ◄──────────────────────────────────────────────────┘
                                                arbiter ──Send() per unassigned item──► escalation_agent ─► synthesizer → END
```

* **Agents propose, the arbiter commits.** The four agents run in parallel and only read their list. They
  return ranked candidates. The Resource Arbiter executes the winning claims through the write tools,
  in order of priority and then timestamp. If two requests claim the same doctor, bed or porter, the
  more urgent or earlier one gets it, and the other request falls back to its next candidate.
* **Conditional spawning.** The Reallocation Worker runs only for ER cases with no free doctor. The
  Staffing Gap Resolver (float pool, then on-call) runs only when no staff member is found. The
  Escalation Agent runs only for items that are still unassigned.
* **Rules.** Emergencies are processed first. A doctor whose shift ends within 30 minutes is not
  assigned, except for ER cases. A discharge-ready bed is released only when ICU/ER is full. Biohazard
  cleaning goes only to the specialized team. Malformed requests and empty batches never crash.

| Request type | Send() targets |
|---|---|
| new_patient | Patient, Doctor, Staff (clerk) |
| er_emergency | Patient, Doctor, Bed (ER), Staff (porter) → Reallocation Worker if no doctor |
| emergency_admission | Patient, Bed (releases discharge-ready bed if ICU/ER full) |
| routine_bed | Patient, Bed (queued if ward full) |
| cleaning | Staff → Housekeeping Dispatcher (biohazard → specialized team) |
| patient_handling | Patient (if identifiable), Staff → Handling Dispatcher |
| malformed | Escalation Agent |

## Layout

```
app.py                      Streamlit entry point
ui/                         sidebar, chat, plan rendering, shift report, architecture tabs
hospital/
  config.py, models.py      paths, rules, pydantic schemas, fixed log schema
  store.py                  CSV-backed lists (seed → data/state), changed only via tools
  tools/                    patient / doctor / bed / staff LangChain tools
  agents/                   the four resource manager agents
  orchestrator/             intake validation, LLM triage, playbook, manager node + Send router
  control/                  arbiter, reallocation, staffing gap, escalation, synthesizer
  graph/                    state + builder
  reporting/                shift log + shift report / archive
  chat/                     message parsing, intent routing, Q&A agent
data/seed, data/requests    provided seed CSVs and request batches
reports/                    archived shift reports from real runs
```

Log schema (`request_log.csv`): `request_id, type, priority, patient, doctor, bed, staff, status,
time_taken, reason`, plus the audit columns `timestamp, description, workers, retry_of, shift_id`.
