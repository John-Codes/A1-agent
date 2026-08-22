from datetime import datetime

from nodes.base import BaseNode
from config import TOOL_ROUNDS
from chat_history_auto_save import save_assistant_message_after_generation
from chat_session_summary import generate_and_save_chat_title_and_summary
from conversation_history import format_recent
from context import load_context_prompt
from llm_client import complete_prompt
from llm_errors import format_attempts
from tools import dispatch_tool_call, parse_tool_calls, strip_tool_calls

class LLMNode(BaseNode):
    def prep(self, shared):
        trigger = shared.get("trigger")
        history = _format_history(shared.get("messages", []), format_recent(20))
        if trigger == "message":
            user_prompt = shared.get("pending_input") or ""
            task = f"User message:\n{user_prompt}"
            system_prompt = load_context_prompt(user_prompt)
        elif trigger == "tick":
            task = (
                "Heartbeat tick. Read your context and decide whether to "
                "reflect, update memory, or do nothing. Do not send a user "
                "message unless a future notify tool exists."
            )
            system_prompt = load_context_prompt(task)
        else:
            raise ValueError(f"Unknown trigger: {trigger}")
        prompt = (
            f"{system_prompt}\n\n"
            f"## Runtime\n{_runtime_context()}\n\n"
            f"## Conversation History\n{history}\n\n"
            f"## Current Task\n{task}"
        )
        return {"prompt": prompt, "trigger": trigger, "shared": shared}

    def exec(self, prep_res):
        prompt = prep_res["prompt"]
        response_text = ""
        for _ in range(TOOL_ROUNDS):
            result = complete_prompt(prompt, prep_res["shared"])
            if not result["ok"]:
                raise RuntimeError(format_attempts(prep_res["shared"]["last_llm_attempts"]))
            response_text = result["text"]
            calls = parse_tool_calls(response_text)
            if not calls:
                return response_text
            tool_results = []
            for call in calls:
                result = dispatch_tool_call(call)
                tool_results.append(_format_tool_result(call, result))
            prompt = _prompt_with_tool_results(prompt, response_text, tool_results)
        return response_text

    def post(self, shared, prep_res, exec_res):
        clean_response = strip_tool_calls(exec_res)
        display_response = clean_response
        if prep_res["trigger"] == "message":
            user_text = shared.get("pending_input") or ""
            shared["messages"].append({"role": "user", "content": user_text})
            shared["messages"].append({"role": "assistant", "content": clean_response})
            session_id = save_assistant_message_after_generation(shared, clean_response)
            generate_and_save_chat_title_and_summary(session_id)
        shared["pending_response"] = display_response
        shared["pending_input"] = None
        shared["pending_image_data"] = None
        return "default"

def _runtime_context():
    today = datetime.now().strftime("%A, %B %d, %Y")
    return f"Current date: {today}. For latest/current facts, use web_search before answering."

def _format_tool_result(call, result):
    return f"<tool_result name=\"{call['name']}\">\n{result}\n</tool_result>"

def _prompt_with_tool_results(prompt, response_text, tool_results):
    return (
        f"{prompt}\n\n"
        f"## Assistant Tool Request\n{response_text}\n\n"
        f"## Tool Results\n{chr(10).join(tool_results)}\n\n"
        "Use the tool results to answer. Do not repeat XML tool tags unless "
        "another tool call is still required."
    )

def _format_history(messages, durable):
    live = "\n".join(f"{m['role']}: {m['content']}" for m in messages[-20:])
    live = live or "(empty)"
    return f"Durable history:\n{durable}\n\nLive session:\n{live}"
