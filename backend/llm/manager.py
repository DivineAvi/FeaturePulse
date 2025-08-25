from collections import defaultdict
from typing import Dict, List

from openai.types.responses import Response, ResponseFunctionToolCall
from config import CONFIG
from openai import OpenAI

class SafeDict(defaultdict):
    def __missing__(self, key):
        return "{" + key + "}"


class llm:
    instance = None
    client: OpenAI
    MODEL = "gpt-3.5-turbo"

    def __init__(self):
        self.client = OpenAI(api_key=CONFIG.OPENAI_API_KEY)

    def chat(
        self,
        question: str,
        chat_history: List[Dict[str, str]] = None,
        system_prompt: str = "You are a helpful assistant , Answer user's question. Chat history: {chat_history}, Question: {question}",
        context: str = "",
        tools_available=[],
    ) -> Dict[str, str]:

        system_prompt = system_prompt.format_map(
            SafeDict(str, chat_history=chat_history, question=question, context=context)
        )

        response = self.client.responses.create(
            model=self.MODEL, input=system_prompt, tools=tools_available
        )
        print(response)
        result = self.handle_response(response)

        return {"tool_call": result['tool_call'],"tool_name":result['tool_name'], "reply": result['reply'], "args": result['args']}

    def handle_response(self, response: Response):
        reply = None
        args = None
        tool_call = False
        tool_name = None

        for o in response.output:
            # ✅ Extract text
            if hasattr(o, "content") and o.content:
                reply = o.content[0].text

            # ✅ Extract tool call
            if isinstance(o, ResponseFunctionToolCall):
                tool_call = True
                args = o.arguments
                tool_name = o.name

        return {"tool_call": tool_call , "tool_name":tool_name, "reply": reply, "args": args}


LLM = llm();

if __name__ == "__main__":
 

    tools = [
        {
            "type": "function",
            "name": "calculator",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    ]

    result = LLM.chat(
        "Add 5 + 7 using the calculator function and also explain what you are doing.",
        tools_available=tools,
    )

    print("=== LLM OUTPUT ===")
    print(result)
