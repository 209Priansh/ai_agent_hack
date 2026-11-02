# ai_agent_hack
Can Hackers Control Your AI Agent?

Imagine you have built an AI agent that can read your emails, access your database and send emails on your behalf.

Now imagine someone sends you a simple email containing hidden instructions.

Your AI agent reads that email and starts following the attacker's instructions instead of yours.

This is called Prompt Injection.

The scary part? The attacker may not need your password. They may only need to manipulate the instructions your AI agent follows."

----------------------------------------------------------------------------------------------------------------
OPEN Terminal in VScode under the project and follow below command :

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install langgraph langchain-core fastapi httpx uvicorn
python demo.py      # Windows PowerShell: $env:PYTHONPATH="."; python demo.py
uvicorn server:app --reload      # then open http://127.0.0.1:8000/docs
