import logging
import textwrap
from typing import List

from automata.config.base import LLMProvider
from automata.core.agent.tool.registry import AutomataOpenAIAgentToolBuilderRegistry
from automata.core.base.agent import AgentToolBuilder, AgentToolProviders
from automata.core.base.tool import Tool
from automata.core.embedding.symbol_similarity import SymbolSimilarity
from automata.core.llm.providers.openai import OpenAIAgentToolBuilder, OpenAITool
from automata.core.symbol.search.symbol_search import SymbolSearch

logger = logging.getLogger(__name__)


class ContextOracleTool(AgentToolBuilder):
    """
    ContextOracleTool is responsible for managing context oracle tools.
    """

    def __init__(
        self,
        symbol_search: SymbolSearch,
        symbol_doc_similarity: SymbolSimilarity,
    ) -> None:
        """
        Initializes ContextOracleTool with given SymbolSearch, SymbolSimilarity.

        Args:
            symbol_search (SymbolSearch): The symbol search object.
            symbol_doc_similarity (SymbolSimilarity): The symbol doc similarity object.
        """
        self.symbol_search = symbol_search
        self.symbol_doc_similarity = symbol_doc_similarity

    def build(self) -> List[Tool]:
        """
        Builds the tools associated with the context oracle.

        Returns:
            List[Tool]: The list of built tools.
        """
        return [
            Tool(
                name="context-oracle",
                function=self._context_generator,
                description=textwrap.dedent(
                    """
                This tool combines SymbolSearch and SymbolSimilarity to create contexts. Given a query, it uses SymbolSimilarity calculate the similarity between each symbol's documentation and the query returns the most similar document. Then, it leverages SymbolSearch to combine Semantic Search with PageRank to find the most relevant symbols to the query. The overview documentation of these symbols is then concated to the result of the SymbolSimilarity query to create a context.

                For instance, if a query reads 'Tell me about SymbolRank', it will find the most similar document to this query from the embeddings, which in this case would be the documentation for the SymbolRank class. Then, it will use SymbolSearch to fetch some of the most relevant symbols which would be 'Symbol', 'SymbolSearch', 'SymbolGraph', etc. This results in a comprehensive context for the query.
                """
                ),
            )
        ]

    def _context_generator(self, query: str, max_related_symbols=5) -> str:
        """
        The generate the context corresponding to a query.

        Args:
            query (str): The query string.

        Returns:
            str: The processed result.
        """
        doc_output = self.symbol_doc_similarity.get_query_similarity_dict(query)
        most_similar_doc_embedding = self.symbol_doc_similarity.embedding_handler.get_embedding(
            sorted(doc_output.items(), key=lambda x: -x[1])[0][0]
        )
        rank_output = self.symbol_search.symbol_rank_search(query)

        result = most_similar_doc_embedding.source_code

        result += most_similar_doc_embedding.embedding_source

        counter = 0
        for symbol, _ in rank_output:
            if counter >= max_related_symbols:
                break
            try:
                result += "%s\n" % symbol.dotpath
                result += self.symbol_doc_similarity.embedding_handler.get_embedding(
                    symbol
                ).summary
                counter += 1
            except Exception as e:
                logger.error(
                    "Failed to get embedding for symbol %s with error: %s",
                    symbol,
                    e,
                )
                continue
        logger.debug(f"ContextOracleTool is returning this result: {result}")
        return result


@AutomataOpenAIAgentToolBuilderRegistry.register_tool_manager
class ContextOracleOpenAIToolBuilder(ContextOracleTool, OpenAIAgentToolBuilder):
    TOOL_TYPE = AgentToolProviders.CONTEXT_ORACLE
    PLATFORM = LLMProvider.OPENAI

    def build_for_open_ai(self) -> List[OpenAITool]:
        tools = super().build()

        # Predefined properties and required parameters
        properties = {
            "query": {"type": "string", "description": "The query string to search for."},
            "max_related_symbols": {
                "type": "integer",
                "description": "The maximum number of related symbols to return.",
            },
        }
        required = ["query"]

        openai_tools = []
        for tool in tools:
            openai_tool = OpenAITool(
                function=tool.function,
                name=tool.name,
                description=tool.description,
                properties=properties,
                required=required,
            )
            openai_tools.append(openai_tool)

        return openai_tools
