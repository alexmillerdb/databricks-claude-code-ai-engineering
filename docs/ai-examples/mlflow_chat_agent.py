"""
Databricks recommends using the MLflow ChatAgent interface to author production-grade agents.

The ChatAgent interface provides a chat schema specification that is similar to, but not strictly compatible with, the OpenAI ChatCompletion schema.

Key benefits of using ChatAgent include:
- Advanced agent capabilities, including multi-agent support.
- Streaming output: Enable interactive user experiences by streaming output in smaller chunks.
- Comprehensive tool-calling message history: Return multiple messages, including intermediate tool-calling messages, for improved quality and conversation management.
- Tool-calling confirmation support.
- Streamlined development, deployment, and monitoring.

Additional features:
- Framework-agnostic: Wrap any existing agent using the ChatAgent interface for out-of-the-box compatibility with AI Playground, Agent Evaluation, and Agent Monitoring.
- Typed authoring interfaces: Write agent code using typed Python classes, benefiting from IDE and notebook autocomplete.
- Automatic signature inference: MLflow automatically infers ChatAgent signatures when logging the agent, simplifying registration and deployment.
- AI Gateway-enhanced inference tables: AI Gateway inference tables are automatically enabled for deployed agents, providing access to detailed request log metadata.
"""

from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatAgentResponse, ChatAgentChunk
import uuid

class MyWrappedAgent(ChatAgent):
    """
    Example wrapper for integrating a custom agent with the MLflow ChatAgent interface.

    This class demonstrates how to adapt an existing agent to the MLflow ChatAgent API,
    enabling compatibility with MLflow's chat schema, streaming, and deployment features.

    Args:
        agent: The underlying agent object that implements an `invoke` method for single-turn
               inference and optionally a `stream` method for streaming responses.

    Methods:
        predict(messages, context=None, custom_inputs=None):
            Handles a single chat completion request. Converts the MLflow chat message format
            to the agent's expected input, invokes the agent, and returns a ChatAgentResponse.

        predict_stream(messages, context=None, custom_inputs=None):
            Handles streaming chat completions. Yields ChatAgentChunk objects as the agent
            produces output, enabling real-time streaming to clients.
    """

    def __init__(self, agent):
        """
        Initialize the wrapped agent.

        Args:
            agent: The underlying agent instance to wrap.
        """
        self.agent = agent

    def predict(self, messages, context=None, custom_inputs=None):
        """
        Generate a chat response using the wrapped agent.

        Args:
            messages (List[ChatAgentMessage]): The conversation history as a list of messages.
            context (ChatContext, optional): Optional context for the agent.
            custom_inputs (dict, optional): Additional custom inputs.

        Returns:
            ChatAgentResponse: The agent's response in MLflow's chat schema.
        """
        # Convert messages to your agent's format
        agent_input = ...  # build from messages
        agent_output = self.agent.invoke(agent_input)
        # Convert output to ChatAgentMessage
        return ChatAgentResponse(
            messages=[
                ChatAgentMessage(
                    role="assistant",
                    content=agent_output,
                    id=str(uuid.uuid4()),
                )
            ]
        )

    def predict_stream(self, messages, context=None, custom_inputs=None):
        """
        Stream chat response chunks from the wrapped agent.

        Args:
            messages (List[ChatAgentMessage]): The conversation history as a list of messages.
            context (ChatContext, optional): Optional context for the agent.
            custom_inputs (dict, optional): Additional custom inputs.

        Yields:
            ChatAgentChunk: Chunks of the agent's response for streaming.
        """
        # If your agent supports streaming
        for chunk in self.agent.stream(...):
            yield ChatAgentChunk(
                delta=ChatAgentMessage(
                    role="assistant",
                    content=chunk,
                    id=str(uuid.uuid4())
                )
            )