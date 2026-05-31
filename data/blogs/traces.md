Tracing

We’re excited to announce native tracing support in LangChain! By enabling tracing in your LangChain runs, you’ll be able to more effectively visualize, step through, and debug your chains and agents.


A view of a more complicated trace at a high level
Motivation

Reasoning about your chain and agent executions is important for troubleshooting and debugging. However, it can be difficult for complex chains and agents, for a number of reasons:

There could be a high number of steps, making it hard to keep track of all of them
The sequence of steps could not be fixed, and could vary based on user input
The inputs/outputs at each stage may not be long and deserve more detailed inspection
Each step of a chain or agent might also involve nesting — for example, an agent might invoke a tool, which uses an LLMMathChain, which uses an LLMChain, which then invokes an LLM. If you notice strange or incorrect output from a top-level agent run, it is difficult to determine exactly where in the execution it was introduced.

Tracing solves this by allowing you to clearly see the inputs and outputs of each LangChain primitive involved in a particular chain or agent run, in the order in which they were invoked.

There has been some great work already for tracing and visualization for LLM compositions (see ICE and langchain-visualizer), and we’re now excited to incorporate tracing natively in LangChain. We hope to release new and exciting features that build upon tracing in the near future.

Usage

As a starting point, we’re allowing everyone to leverage tracing in their LangChain compositions by using a locally hosted setup spun up by docker-compose. We’re also rolling out a hosted version to a small initial group of users. If you are interested in getting access to this, please fill out this form.

For full technical documentation on how to get started, please see here.

We hope to continuously iterate on this to make it as useful as possible. Please reach out with any feedback!

Up Next

We’re just getting started with tracing and additional features. In the future we hope to add:

UI improvements
Better filtering and grouping of traces
Logging the full serialized LLM and Chain for each run
Other exciting features we’re still fleshing out ;)
LangSmith, our agent engineering platform, helps developers debug every agent decision, eval changes, and deploy in one click.