import os
import random
from unittest.mock import Mock

import numpy as np
import pytest

from automata_docs.core.embedding.code_embedding import SymbolCodeEmbeddingHandler
from automata_docs.core.embedding.symbol_similarity import SymbolSimilarity
from automata_docs.core.symbol.graph import SymbolGraph
from automata_docs.core.symbol.parser import parse_symbol
from automata_docs.core.symbol.search.rank import SymbolRankConfig
from automata_docs.core.symbol.search.symbol_search import SymbolSearch


@pytest.fixture
def temp_output_filename():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "test_output.json")
    yield filename
    if os.path.exists(filename):
        os.remove(filename)


prefix = "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `config.automata_agent_config`/"


@pytest.fixture
def mock_simple_method_symbols(monkeypatch):
    return [parse_symbol(prefix + str(random.random()) + "_uri_ex_method().") for _ in range(100)]


@pytest.fixture
def mock_simple_class_symbols():
    return [parse_symbol(prefix + str(random.random()) + "_uri_ex_method#") for _ in range(100)]


@pytest.fixture
def mock_embedding(monkeypatch):
    return np.array([random.random() for _ in range(1024)])


def get_sem(monkeypatch, temp_output_filename):
    monkeypatch.setattr(
        "automata_docs.core.symbol.symbol_utils.convert_to_fst_object",
        lambda args: "symbol_source",
    )
    return SymbolCodeEmbeddingHandler(temp_output_filename)


def patch_get_embedding(monkeypatch, mock_embedding):
    # Define the behavior of the mock build_embedding function
    mock_get_embedding = Mock(return_value=mock_embedding)
    monkeypatch.setattr("openai.embeddings_utils.get_embedding", mock_get_embedding)


@pytest.fixture
def symbols():
    symbols = [
        # Symbol with a simple attribute
        parse_symbol(
            "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `config.automata_agent_config`/AutomataAgentConfig#description."
        ),
        # Symbol with a method with foreign argument
        parse_symbol(
            "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `config.automata_agent_config`/AutomataAgentConfig#load().(config_name)"
        ),
        # Symbol with a class method, self as argument
        # parse_symbol(
        #     "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `tools.python_tools.python_ast_indexer`/PythonASTIndexer#get_module_path().(self)"
        # ),
        # Symbol with a locally defined object
        parse_symbol(
            "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `core.tasks.automata_task_executor`/logger."
        ),
        # Symbol with a class object and class variable
        parse_symbol(
            "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `config.automata_agent_config`/AutomataAgentConfig#verbose."
        ),
        # Symbol with a function in a module
        # parse_symbol("scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `core.coordinator.tests.test_automata_coordinator`/test().(coordinator)"),
        # Symbol with a class method
        parse_symbol(
            "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `evals.eval_helpers`/EvalAction#__init__().(action)"
        ),
        # Symbol with an object
        parse_symbol(
            "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `core.agent.automata_agent_enums`/ActionIndicator#CODE."
        ),
        # Class Name
        parse_symbol(
            "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `core.agent.automata_agent_enums`/ActionIndicator#"
        ),
        # Init
        parse_symbol(
            "scip-python python automata_docs 75482692a6fe30c72db516201a6f47d9fb4af065 `core.base.tool`/ToolNotFoundError#__init__()."
        ),
    ]

    return symbols


@pytest.fixture
def symbol_graph():
    # assuming the path to a valid index protobuf file, you should replace it with your own file path
    file_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(file_dir, "index.scip")
    graph = SymbolGraph(index_path)
    return graph


@pytest.fixture
def symbol_graph_mock(mocker):
    mock = mocker.MagicMock(spec=SymbolGraph)
    return mock


@pytest.fixture
def symbol_searcher(mocker, symbol_graph_mock):
    symbol_similarity_mock = mocker.MagicMock(spec=SymbolSimilarity)
    symbol_similarity_mock.embedding_handler = mocker.MagicMock(spec=SymbolCodeEmbeddingHandler)
    symbol_rank_config_mock = mocker.MagicMock(spec=SymbolRankConfig)

    return SymbolSearch(
        symbol_graph_mock,
        symbol_similarity_mock,
        symbol_rank_config_mock,
    )
