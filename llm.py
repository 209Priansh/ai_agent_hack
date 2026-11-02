"""A deterministic stand-in for a naive LLM, so the demo runs offline and reproducibly.

It models the core failure mode of prompt injection: the model sees trusted
instructions (user/system) and untrusted data (email bodies) in one flat text
stream, and will follow imperative sentences found in either one.

To use a real model, pass any object with `.invoke(messages) -> AIMessage`
(e.g. a tool-bound chat model) to `run_agent(..., llm=...)`.
"""
import json
import re
import uuid

from langchain_core.messages import AIMessage, ToolMessage


def _call(name, **args):
    return {"name": name, "args": args, "id": uuid.uuid4().hex[:8]}


class NaiveSimulatedLLM:
    FORWARD = re.compile(r"forward the email titled ['\"](.+?)['\"] to ([\w.+-]+@[\w.-]+)", re.I)
    REPLY = re.compile(r"reply to ([\w.+-]+@[\w.-]+) with the message ['\"](.+?)['\"]", re.I)

    def invoke(self, messages):
        tools = [m for m in messages if isinstance(m, ToolMessage)]
        done = {m.name for m in tools}

        # Step 1: list the inbox
        if "read_inbox" not in done:
            return AIMessage(content="", tool_calls=[_call("read_inbox")])

        listing = json.loads(next(m.content for m in tools if m.name == "read_inbox"))

        # Step 2: open every email
        read_ids = {m.tool_call_id for m in tools if m.name == "read_email"}
        if not any(m.name == "read_email" for m in tools):
            return AIMessage(content="", tool_calls=[_call("read_email", email_id=e["id"]) for e in listing])

        # Step 3: the flaw. Instructions found inside email bodies get obeyed.
        if not ({"forward_email", "send_email"} & done):
            for m in tools:
                if m.name != "read_email":
                    continue
                if hit := self.FORWARD.search(m.content):
                    subject, to = hit.group(1), hit.group(2).rstrip(".")
                    target = next((e["id"] for e in listing if e["subject"].lower() == subject.lower()), None)
                    if target:
                        return AIMessage(content="", tool_calls=[_call("forward_email", email_id=target, to=to)])
                if hit := self.REPLY.search(m.content):
                    return AIMessage(content="", tool_calls=[_call(
                        "send_email", to=hit.group(1).rstrip("."), subject="Re: Invoice #8841", body=hit.group(2))])

        # Step 4: summarize
        lines = [f"- {e['from']}: {e['subject']}" for e in listing]
        return AIMessage(content="Inbox summary:\n" + "\n".join(lines))
