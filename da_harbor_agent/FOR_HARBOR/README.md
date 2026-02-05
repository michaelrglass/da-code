To run DA-Code parity experiments using DA-Agent put `da_agent.py` and `install-da-agent.sh.j2` under `src/harbor/agents/installed` in the Harbor source tree.
You will also need to modify `src/harbor/models/agent/name.py` and `src/harbor/agents/factory.py`

Set your OPENAI_API_KEY and if used OPENAI_BASE_URL (for litellm proxy or similar).
Then run:
```bash
harbor run -p ./datasets/dacode \
   --agent da-agent \
   --model gpt-4o \
   --agent-kwarg "repo_path=da-code/da_harbor_agent" \
   --n-concurrent 4
```
