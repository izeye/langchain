"""Question Answering."""
from typing import Dict, List, Any

from pydantic import BaseModel, Extra, Field, root_validator

from langchain.chat.base import BaseChatChain
from langchain.chains.conversation.prompt import PROMPT
from langchain.chains.llm import LLMChain
from langchain.prompts.base import BasePromptTemplate
from langchain.chat.memory import SimpleChatMemory
from langchain.chat_models.base import BaseChat
from langchain.schema import ChatMessage


class QAChain(BaseChatChain, BaseModel):
    """Chain to have a conversation and load context from memory.

    Example:
        .. code-block:: python

            from langchain import ConversationChain, OpenAI
            conversation = ConversationChain(llm=OpenAI())
    """

    model: BaseChat
    """Default memory store."""
    prompt: BasePromptTemplate = PROMPT
    """Default conversation prompt to use."""
    question_key: str = "question"  #: :meta private:
    documents_key: str = "input_documents"  #: :meta private:
    output_key: str = "response"  #: :meta private:
    starter_messages: List[ChatMessage] = Field(default_factory=list)

    @classmethod
    def from_model(cls, model: BaseModel, **kwargs: Any):
        """From model. Future proofing."""
        return cls(model=model, **kwargs)

    @property
    def _chain_type(self) -> str:
        return "chat:qa"

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        new_message = ChatMessage(text = inputs[self.question_key], role=self.human_prefix)
        docs = inputs[self.documents_key]
        doc_messages = [ChatMessage(text=doc.page_content, role=self.human_prefix) for doc in docs]
        messages = self.starter_messages + doc_messages + [new_message]
        output = self.model.run(messages)
        return {self.output_key: output.text}


    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Use this since so some prompt vars come from history."""
        return [self.question_key, self.documents_key]
