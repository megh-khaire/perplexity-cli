"""Tool execution system for LLM function calling."""

import json
from typing import Any, Dict, List

from src.tools.search_tool import SearchTool


class ToolExecutor:
    """Executes tool calls from LLM responses."""

    def __init__(self):
        """Initialize the tool executor with available tools."""
        self.tools: Dict[str, SearchTool] = {}

        # Initialize available tools
        search_tool = SearchTool()
        self.tools[search_tool.function_definition["name"]] = search_tool

    def execute_tool_call(self, tool_call) -> str:
        """Execute a single tool call.

        Args:
            tool_call: OpenAI tool call object with function name and arguments

        Returns:
            String result from the tool execution
        """
        function_name = tool_call.function.name

        if function_name not in self.tools:
            return json.dumps(
                {
                    "error": f"Unknown tool: {function_name}",
                    "available_tools": list(self.tools.keys()),
                }
            )

        try:
            # Parse arguments
            arguments = json.loads(tool_call.function.arguments)

            # Execute the tool
            tool = self.tools[function_name]
            result = tool.execute(**arguments)

            return result

        except json.JSONDecodeError as e:
            return json.dumps(
                {
                    "error": f"Invalid arguments JSON: {str(e)}",
                    "arguments": tool_call.function.arguments,
                }
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Tool execution failed: {str(e)}", "function": function_name}
            )

    def execute_tool_calls(self, tool_calls: List) -> Dict[str, str]:
        """Execute multiple tool calls.

        Args:
            tool_calls: List of OpenAI tool call objects

        Returns:
            Dictionary mapping tool call IDs to their results
        """
        results = {}

        for tool_call in tool_calls:
            result = self.execute_tool_call(tool_call)
            results[tool_call.id] = result

        return results

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tool function definitions for OpenAI."""
        return [
            {"type": "function", "function": tool.function_definition}
            for tool in self.tools.values()
        ]
