"""
Main Tool Use Agent implementation using LangGraph
"""
from typing import Dict, Any, Optional, List, TypedDict, Sequence
import asyncio
import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from openai import OpenAI

from .base import AgentResponse, AgentConfig
from .config import ConfigManager
from ..tools.base import BaseTool, ToolResult
from ..tools.registry import ToolRegistry
from ..context.session import SessionContext, SessionManager, Message
from ..fallback.handler import FallbackChain
from ..fallback.strategies import (
    RetryHandler,
    AlternativeToolHandler,
    FallbackResponseHandler,
    GracefulDegradationHandler
)


class AgentState(TypedDict):
    """Agent state for LangGraph"""
    messages: Sequence[Dict[str, Any]]
    tool_calls: Optional[List[Dict[str, Any]]]
    tool_results: Optional[List[Dict[str, Any]]]
    next_action: Optional[str]


class ToolUseAgent:
    """
    Tool Use Agent with LangGraph integration

    Features:
    - Intelligent tool calling decision
    - Multi-turn conversation context
    - Fallback handling for tool failures
    - LangGraph state management
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        tool_registry: Optional[ToolRegistry] = None,
        session_manager: Optional[SessionManager] = None
    ):
        """
        Initialize Tool Use Agent

        Args:
            config: Agent configuration
            tool_registry: Tool registry instance
            session_manager: Session manager instance
        """
        # Load configuration
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.load_config()

        self.config = config

        # Initialize components
        self.tool_registry = tool_registry or ToolRegistry()
        self.session_manager = session_manager or SessionManager()
        self.fallback_chain = self._setup_fallback_chain()

        # Initialize LLM client
        self.llm_client = self._init_llm_client()

        # Build LangGraph
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()

    def _init_llm_client(self) -> OpenAI:
        """
        Initialize OpenAI client

        Returns:
            OpenAI: Initialized client
        """
        # Try to get credentials from environment first
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1/")

        # Use default credentials from requirements if not in environment
        if not api_key:
            api_key = 'sk-kagazldxzrbgubldmwhwxjyntqbfhxxswafrvjwxczyzvuxo'

        return OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def _setup_fallback_chain(self) -> FallbackChain:
        """
        Setup fallback chain with default handlers

        Returns:
            FallbackChain: Configured fallback chain
        """
        chain = FallbackChain()

        # Add handlers in priority order
        chain.add_handler(RetryHandler(max_retries=self.config.retry_attempts))
        chain.add_handler(AlternativeToolHandler())
        chain.add_handler(GracefulDegradationHandler())
        chain.add_handler(FallbackResponseHandler())

        return chain

    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph for agent workflow

        Returns:
            StateGraph: Built graph
        """
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tool_executor", self._tool_executor_node)

        # Set entry point
        workflow.set_entry_point("agent")

        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_use_tools,
            {
                "tools": "tool_executor",
                "end": END
            }
        )

        # Add edge from tool executor back to agent
        workflow.add_edge("tool_executor", "agent")

        return workflow.compile()

    async def _agent_node(self, state: AgentState) -> AgentState:
        """
        Agent node: Decide whether to use tools and generate response

        Args:
            state: Current agent state

        Returns:
            AgentState: Updated state
        """
        messages = state.get("messages", [])

        # Build system prompt with tool information
        system_prompt = self._build_system_prompt()

        # Prepare messages for LLM
        llm_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            llm_messages.append(msg)

        try:
            # Call LLM
            response = self.llm_client.chat.completions.create(
                model=self.config.model_name,
                messages=llm_messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            assistant_message = response.choices[0].message
            content = assistant_message.content or ""
            tool_calls = assistant_message.tool_calls if assistant_message.tool_calls else None

            # Determine next action
            next_action = "end"
            if tool_calls and len(tool_calls) > 0:
                next_action = "tools"

            return {
                "messages": state["messages"] + [{"role": "assistant", "content": content}],
                "tool_calls": tool_calls,
                "tool_results": state.get("tool_results"),
                "next_action": next_action
            }

        except Exception as e:
            # Handle LLM errors
            error_msg = f"LLM error: {str(e)}"
            return {
                "messages": state["messages"] + [{"role": "assistant", "content": error_msg}],
                "tool_calls": None,
                "tool_results": state.get("tool_results"),
                "next_action": "end"
            }

    async def _tool_executor_node(self, state: AgentState) -> AgentState:
        """
        Tool executor node: Execute tool calls

        Args:
            state: Current agent state

        Returns:
            AgentState: Updated state
        """
        tool_calls = state.get("tool_calls", [])
        tool_results = []

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = eval(tool_call.function.arguments)

            try:
                # Execute tool
                result = await self.tool_registry.execute_tool(tool_name, **tool_args)

                # Format result for LLM
                if result.success:
                    tool_result = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "tool_name": tool_name,
                        "content": result.to_formatted_string()
                    }
                else:
                    # Tool failed, use fallback handling
                    context = {
                        "tool_registry": self.tool_registry,
                        "tool_name": tool_name,
                        "tool_params": tool_args,
                        "user_query": state["messages"][-1].get("content", "")
                    }

                    fallback_response = await self.fallback_chain.handle_error(
                        Exception(result.error or "Tool execution failed"),
                        context
                    )

                    tool_result = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "tool_name": tool_name,
                        "content": fallback_response
                    }

                tool_results.append(tool_result)

            except Exception as e:
                # Tool execution error
                context = {
                    "tool_registry": self.tool_registry,
                    "tool_name": tool_name,
                    "tool_params": tool_args,
                    "user_query": state["messages"][-1].get("content", "")
                }

                fallback_response = await self.fallback_chain.handle_error(e, context)

                tool_result = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "tool_name": tool_name,
                    "content": fallback_response
                }

                tool_results.append(tool_result)

        return {
            "messages": state["messages"] + tool_results,
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "next_action": "agent"
        }

    def _should_use_tools(self, state: AgentState) -> str:
        """
        Decide whether to use tools

        Args:
            state: Current agent state

        Returns:
            str: Next action ("tools" or "end")
        """
        tool_calls = state.get("tool_calls")
        if tool_calls and len(tool_calls) > 0:
            return "tools"
        return "end"

    def _build_system_prompt(self) -> str:
        """
        Build system prompt with tool information

        Returns:
            str: System prompt
        """
        prompt = """You are a helpful AI assistant with access to various tools.

Your task is to:
1. Understand the user's request
2. Decide if you need to use tools to fulfill the request
3. Execute tools when necessary
4. Provide helpful and accurate responses

Available tools:
"""

        # Add tool descriptions
        for tool_name, tool in self.tool_registry.get_all().items():
            prompt += f"\n- {tool_name}: {tool.description}"
            if tool.parameters:
                params = ", ".join([f"{name} ({param.type})" for name, param in tool.parameters.items()])
                prompt += f"\n  Parameters: {params}"

        prompt += """

When to use tools:
- When the user asks for specific information you don't have
- When the user requests actions that require external services
- When you need to perform calculations or data processing

When NOT to use tools:
- For general conversation
- When you can answer from your knowledge
- When the request is ambiguous (ask for clarification first)

Always provide helpful, clear, and accurate responses to the user."""

        return prompt

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> AgentResponse:
        """
        Process user message

        Args:
            message: User input message
            session_id: Optional session ID

        Returns:
            AgentResponse: Agent response
        """
        # Get or create session
        if not session_id:
            session_id = f"session_{asyncio.get_event_loop().time() * 1000}"

        session = self.session_manager.get_session(session_id)
        if not session:
            session = self.session_manager.create_session(session_id)

        # Add user message to session
        session.add_user_message(message)

        # Prepare state for LangGraph
        messages = session.get_messages_for_llm(limit=self.config.max_context_messages)
        state = {
            "messages": messages,
            "tool_calls": None,
            "tool_results": None,
            "next_action": None
        }

        try:
            # Run graph
            config = RunnableConfig(
                configurable={"thread_id": session_id},
                recursion_limit=50
            )

            result = await self.graph.ainvoke(state, config)

            # Extract final response
            final_messages = result.get("messages", [])
            assistant_message = None
            for msg in reversed(final_messages):
                if msg.get("role") == "assistant":
                    assistant_message = msg
                    break

            if not assistant_message:
                raise Exception("No assistant message in result")

            # Add assistant message to session
            session.add_assistant_message(
                content=assistant_message.get("content", ""),
                tool_calls=result.get("tool_calls")
            )

            # Create response
            return AgentResponse(
                content=assistant_message.get("content", ""),
                tool_calls=result.get("tool_calls"),
                tool_results=result.get("tool_results"),
                metadata={"session_id": session_id},
                success=True
            )

        except Exception as e:
            # Handle errors
            error_response = await self.fallback_chain.handle_error(
                e,
                {"user_query": message, "include_error_details": False}
            )

            return AgentResponse(
                content=error_response,
                metadata={"session_id": session_id},
                success=False,
                error=str(e)
            )

    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a new tool

        Args:
            tool: Tool to register
        """
        self.tool_registry.register(tool)

    def get_session_context(self, session_id: str) -> Optional[SessionContext]:
        """
        Get session context

        Args:
            session_id: Session ID

        Returns:
            SessionContext: Session context or None
        """
        return self.session_manager.get_session(session_id)

    def list_tools(self) -> List[str]:
        """
        List all available tools

        Returns:
            List[str]: Tool names
        """
        return self.tool_registry.list_tools()

    def clear_session(self, session_id: str) -> bool:
        """
        Clear session messages

        Args:
            session_id: Session ID

        Returns:
            bool: True if session was cleared
        """
        session = self.session_manager.get_session(session_id)
        if session:
            session.clear_messages()
            return True
        return False