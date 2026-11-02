from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from agent import run_agent
from mailbox import Mailbox

app = FastAPI(title="Sandboxed email agent (prompt-injection demo)")


class RunRequest(BaseModel):
    task: str = "Summarize my inbox."
    mode: Literal["vulnerable", "allowlist", "hardened"] = "vulnerable"
    scenario: Literal["none", "exfil", "internal"] = "exfil"


@app.get("/inbox")
def inbox(scenario: Literal["none", "exfil", "internal"] = "exfil"):
    """Preview the mock inbox, including the malicious email for the scenario."""
    return Mailbox(scenario).emails


@app.post("/run")
def run(req: RunRequest):
    return run_agent(req.task, req.mode, req.scenario)
