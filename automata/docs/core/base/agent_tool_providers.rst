AgentToolProviders
==================

``AgentToolProviders`` is a base class for providing tools that can be
utilized by an Automata agent. The main symbols related to this class
include ``AgentConfigName``, ``Tool``,
``LLMConversationDatabaseProvider``, ``LLMIterationResult``, and
``LLMPlatforms``.

Overview
--------

``AgentToolProviders`` is used to create sets of tools specific to the
agent, which the agent can use to interact with different tasks. Tools
can be added to the agent or replaced using the provided methods, and
the agent’s behavior can change based on the tools it has access to.

Related Symbols
---------------

-  ``automata.config.config_types.AgentConfigName``
-  ``automata.core.base.tool.Tool``
-  ``automata.core.llm.completion.LLMConversationDatabaseProvider``
-  ``automata.core.llm.completion.LLMIterationResult``
-  ``automata.core.llm.providers.available.LLMPlatforms``
-  ``automata.core.agent.tool.tool_utils.AgentToolFactory``
-  ``automata.core.agent.tool.builder.py_writer.PyWriterOpenAIToolBuilder``
-  ``automata.core.agent.tool.builder.symbol_search.SymbolSearchOpenAIToolBuilder``
-  ``automata.core.agent.tool.registry.AutomataOpenAIAgentToolBuilderRegistry``

Example
-------

The following example demonstrates how to create a custom tool and add
it to an agent using ``AgentToolProviders``.

.. code:: python

   from automata.core.base.agent import AgentToolProviders

   class CustomTool(AgentToolProviders):
       def __init__(self):
           super().__init__()
           self.tools = []

       def add_tool(self, tool):
           self.tools.append(tool)

   # Create an instance of CustomTool and add an example tool
   my_tool_providers = CustomTool()
   example_tool = lambda x: "Example tool response"
   my_tool_providers.add_tool(example_tool)

   # Use the example tool in the agent
   response = my_tool_providers.tools[0]("input")
   print(response)  # Output: Example tool response

Limitations
-----------

The primary limitation of ``AgentToolProviders`` is that it requires
manual creation and management of tools. Creating and adding tools, as
well as updating tool behavior or availability, must be manually
completed by the developer. Additionally, some tools may depend on
external services or libraries that could limit their functionality in
different environments.

Follow-up Questions:
--------------------

-  Is there a way to automate the process of tool creation or management
   within ``AgentToolProviders``?
-  How can we ensure that all necessary dependencies and services are
   available for the tools used by the agent?
