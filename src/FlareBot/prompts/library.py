"""
Prompt Library Module for Flare AI RAG

This module provides a centralized management system for AI prompts used throughout
the Flare AI RAG application. It handles the organization, storage, and retrieval
of various prompt templates used for different operations like token transactions,
account generation, and user interactions.

The module implements a PromptLibrary class that maintains a collection of Prompt
objects, each representing a specific type of interaction or operation template.
Prompts are categorized for easy management and retrieval.
"""

import structlog

from FlareBot.prompts.schemas import (
    Prompt,
    RAGRouterResponse,
    SemanticRouterResponse,
)
from FlareBot.prompts.templates import (
    CONVERSATIONAL,
    RAG_RESPONDER,
    RAG_ROUTER,
    REMOTE_ATTESTATION,
    SEMANTIC_ROUTER,
)

logger = structlog.get_logger(__name__)


class PromptLibrary:
    """
    A library for managing and organizing AI prompts used in the Flare AI RAG.

    This class serves as a central repository for all prompt templates used in
    the application. It provides functionality to add, retrieve, and categorize
    prompts for various operations such as token transactions, account management,
    and user interactions.

    Attributes:
        prompts (dict[str, Prompt]): Dictionary storing prompt objects
            with their names as keys.
    """

    def __init__(self) -> None:
        """
        Initialize a new PromptLibrary instance.

        Creates an empty prompt dictionary and populates it with default prompts
        through the _initialize_default_prompts method.
        """
        self.prompts: dict[str, Prompt] = {}
        self._initialize_default_prompts()

    def _initialize_default_prompts(self) -> None:
        """
        Initialize the library with a set of default prompts.

        Creates and adds the following default prompts:
        - semantic_router: For routing user queries
        - token_send: For token transfer operations
        - token_swap: For token swap operations
        - generate_account: For wallet generation
        - conversational: For general user interactions
        - request_attestation: For remote attestation requests
        - tx_confirmation: For transaction confirmation

        This method is called automatically during instance initialization.
        """
        default_prompts = [
            Prompt(
                name="semantic_router",
                description="Route user query based on user input",
                template=SEMANTIC_ROUTER,
                required_inputs=["user_input"],
                response_mime_type="text/x.enum",
                response_schema=SemanticRouterResponse,
                category="router",
            ),
            Prompt(
                name="conversational",
                description="Converse with a user",
                template=CONVERSATIONAL,
                required_inputs=["user_input"],
                response_schema=None,
                response_mime_type=None,
                category="conversational",
            ),
            Prompt(
                name="rag_router",
                description="The ",
                template=RAG_ROUTER,
                required_inputs=["user_input"],
                response_mime_type="application/json",
                response_schema=RAGRouterResponse,
                category="rag-router",
            ),
            Prompt(
                name="rag_responder",
                description="The ",
                template=RAG_RESPONDER,
                required_inputs=["user_input"],
                response_schema=None,
                response_mime_type=None,
                category="conversational",
            ),
            Prompt(
                name="request_attestation",
                description="User has requested a remote attestation",
                template=REMOTE_ATTESTATION,
                required_inputs=None,
                response_schema=None,
                response_mime_type=None,
                category="conversational",
            ),
        ]

        for prompt in default_prompts:
            self.add_prompt(prompt)

    def add_prompt(self, prompt: Prompt) -> None:
        """
        Add a new prompt to the library.

        Args:
            prompt (Prompt): The prompt object to add to the library.

        Logs:
            Debug log entry when prompt is successfully added.

        Example:
            ```python
            custom_prompt = Prompt(name="custom", template="...", category="misc")
            library.add_prompt(custom_prompt)
            ```
        """
        self.prompts[prompt.name] = prompt
        logger.debug("prompt_added", name=prompt.name, category=prompt.category)

    def get_prompt(self, name: str) -> Prompt:
        """
        Retrieve a prompt by its name.

        Args:
            name (str): The name of the prompt to retrieve.

        Returns:
            Prompt: The requested prompt object.

        Raises:
            KeyError: If the prompt name doesn't exist in the library.

        Example:
            ```python
            try:
                prompt = library.get_prompt("token_send")
            except KeyError:
                print("Prompt not found")
            ```
        """
        if name not in self.prompts:
            logger.error("prompt_not_found", name=name)
            msg = f"Prompt '{name}' not found in library"
            raise KeyError(msg)
        return self.prompts[name]

    def get_prompts_by_category(self, category: str) -> list[Prompt]:
        """
        Get all prompts in a specific category.

        Args:
            category (str): The category to filter prompts by.

        Returns:
            list[Prompt]: A list of all prompts in the specified category.
        """
        return [
            prompt for prompt in self.prompts.values() if prompt.category == category
        ]

    def list_categories(self) -> list[str]:
        """
        List all available prompt categories.

        Returns:
            list[str]: A list of unique category names used in the library.

        Example:
            ```python
            categories = library.list_categories()
            print("Available categories:", categories)
            ```
        """
        return list(
            {
                prompt.category
                for prompt in self.prompts.values()
                if prompt.category is not None
            }
        )
