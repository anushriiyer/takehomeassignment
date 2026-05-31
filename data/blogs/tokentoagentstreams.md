From Token Streams to Agent Streams
Key Takeaways

Streaming needs to evolve beyond tokens
Modern agents generate messages, tool calls, subagent activity, state changes, approvals, and media, requiring structured event streams instead of flat text output.
Typed events and projections simplify frontend development
Applications subscribe directly to messages, tool calls, state, subagents, or custom channels while the runtime handles assembly, ordering, and reconnection.
Scoped subscriptions make complex agent UIs scalable
Frontends only stream the parts of the agent tree they render, enabling efficient subagent inspectors, dashboards, and long-running production workloads.
One streaming model works across runtimes and modalities
The same architecture powers local and remote runs, React/Vue/Svelte/Angular SDKs, and supports text, tools, images, audio, video, and custom application events.
The agents people are building now do a lot. A single Deep Agents run can plan, delegate to subagents, call tools, pause for human approval, and produce text, structured data, or media along the way. Every one of those steps is something a user might want to see as it happens.

Streaming APIs designed for one model call and one stream of tokens can't carry that. Once an agent fans out across a graph, the frontend needs more than token deltas. It needs to know which step produced each event, how to subscribe to just the subagent on screen, and how to reconnect after a browser refresh without replaying everything.

The latest Deep Agents, LangChain, and LangGraph streaming work is designed around application events instead of raw chunks. Each event is typed and tagged by where in the agent tree it came from; applications iterate projections like messages, tool calls, or subagent statuses; the same model carries from local runs to remote threads to React, Vue, Svelte, and Angular SDKs. Alongside the release, we're publishing a streaming cookbook with runnable Python and TypeScript examples.

The Requirements

Consider a research agent that delegates to three subagents, each calling tools, updating state, and streaming intermediate findings. A useful product UI might want to render the main answer token-by-token, each subagent's status, tool calls as they assemble, and any media the agent generates.

Flattening all of that into one stream pushes too much work onto application developers. If the streaming layer absorbs that complexity, the questions worth asking move past "can I show tokens?" to:

Can I render a live tree of agent work?
Can I subscribe to one subagent without downloading every other subagent's output?
Can I stream reasoning, tool calls, state, and media with explicit structure rather than concatenated chunks?
Can I surface human approval requests as first-class events?
Can I reconnect to a running thread and pick up where it left off?
Can I add custom domain-specific streams without forking the runtime?
Can I use the same concepts locally, remotely, and in a frontend framework?

Typed streams turn agent execution into structured application events: enabling text, tools, media, reasoning, code, and subagents to stream independently.
Streaming for chat completions and single model calls is a solved problem. The next layer is streaming for graph-shaped, tool-using, stateful, interruptible, multimodal agents that run across backends and frontends.

The Solution

The new streaming primitives are built around four ideas:

Typed events instead of raw chunks.
Each event arrives labelled with what kind of work it describes (a message, a tool call, a state change, a subagent status) and where in the agent tree it came from.
Projections instead of parsing.
Applications iterate the views they want to render: messages, tool calls, subagent statuses, custom channels. The runtime handles assembly, reordering, and reconnection.
Scoped subscriptions.
Clients ask only for the channels and parts of the agent tree they're rendering, so a subagent inspector doesn't pull every subagent's tokens.
The same model across runtimes.
Local graph runs, remote threads, and React/Vue/Svelte/Angular components all speak the same protocol, with projections at the bottom and hooks at the top.
A Typed Event Protocol

The new streaming foundation starts with a common event envelope. Instead of opaque stream tuples, you get structured events labelled with what kind of work they describe and where in the agent tree they came from.

Channels describe the concern being streamed:

messages for transcript and content-block deltas
values and updates for graph state
tools for tool execution lifecycle
lifecycle for runs, subgraphs, and subagents
checkpoints for branching and time travel
custom:* for application-defined projections
Namespaces describe where the event happened in the agent tree. The root graph, a nested subgraph, and a Deep Agents subagent can all emit the same channel type without losing their identity.

That separation is the key design choice: channels are reusable concerns, while namespaces identify the part of the run producing them.

Projections: The API Developers Actually Want

Most application code should not iterate over raw protocol events. It should ask for the thing it wants to render.

Runs do exactly that, exposing typed projections on top of the event stream:

run = await graph.astream_events(
    {"messages": [{"role": "user", "content": "Research LangChain streaming"}]},
    version="v3",
)
 
async for message in run.messages:
    async for delta in message.text:
        sys.stdout.write(delta)
 
final_state = await run.output()
Each message arrives as typed content blocks such as text, reasoning, tool-call arguments, and usage data, instead of a stream of strings that applications need to stitch back together.

That matters for modern model output. Reasoning should be rendered differently from final answer text. Tool-call arguments need to be assembled as structured data. Usage and output metadata should survive the streaming path. Multimodal data should not be forced through a text-only interface.

Subagents and Subgraphs

The same projection pattern applies beyond messages. LangGraph is the runtime layer that lets developers structure agents as graphs of nodes, including nested subgraphs. Deep Agents sits on top of it and adds a higher-level delegation model where an agent can hand work off to a subagent. Streaming needs to make both visible without collapsing them into one flat transcript.

The new primitives distinguish subgraphs from subagents:

Subgraphs surface for any nested graph execution.
Subagents surface today when an agent delegates via the Deep Agents task call.
async for subagent in run.subagents:
    print(f"{subagent.name}: {subagent.status}")
 
    async for message in subagent.messages:
        async for delta in message.text:
            sys.stdout.write(delta)
Both arrive as lightweight handles you can read identity, position, and status off of. The detailed messages, tool calls, and state changes only stream when something in your UI asks for them.

This enables UIs that scale with agent complexity. A dashboard built on Deep Agents can show a list of running subagents for free, then open message and tool streams only for the selected one. A research product can show high-level progress across a tree of work without paying the wire cost for every token produced by every worker.

For developers, this is the practical shift: streaming is no longer a low-level transport detail that each app has to parse. It is an application API.

Custom Channels

Not every useful stream is a built-in channel. Applications often need domain-specific projections: citations, progress events, structured plans, UI descriptions, media handles, workflow metrics, or anything else the product wants to render live.

Streaming transformers are small classes that filter protocol events and push derived items into a named channel. The ToolActivityTransformer here watches the messages channel for tool-call starts and exposes the result as a toolActivity extension. See Build your own projection for the full pattern.

run = await graph.astream_events(
    input,
    version="v3",
    transformers=[ToolActivityTransformer],
)
 
async for activity in run.extensions["toolActivity"]:
    print(activity)
On the frontend, the same idea appears as extension selectors:

const stream = useStream({
  assistantId: "agent",
  apiUrl: "<http://localhost:2024>",
});
 
const uiEvent = useExtension(stream, "a2ui");
The cookbook includes a generative UI example where an agent emits declarative A2UI messages over a `custom:a2ui` channel. The React app subscribes to that extension and renders live interface surfaces as the agent produces them. This is the pattern we expect to become common: agents streaming product-specific state, not just assistant text.

One Event Log, Many Views

Agent UIs often need multiple live views of the same run. A chat panel renders the main answer. A side panel renders subagent activity. A debugger renders raw events. A progress bar watches state. An analytics layer records tool usage.

Those views should not compete to drain the same stream.

The new runtime model supports multiple projections over the same underlying event log. You can consume messages, values, tool calls, subgraphs, and custom extensions independently. Adding a progress view does not require rewriting the chat stream. Adding a subagent inspector does not mean shipping every subagent token to every component.

Remote streaming uses the same idea. A client can subscribe to exactly the channels and namespaces it needs:

const thread = client.threads.stream({
  assistantId: "research-agent",
});
 
await thread.subscribe({
  channels: ["messages", "tools", "values", "lifecycle"],
  namespaces: [["researcher"]],
  depth: 2,
});
Events carry ordering metadata so clients can reconnect and replay from the last seen point. If a browser refreshes while an agent is still running, the UI can reattach to the thread, catch up on buffered events, and continue with live updates instead of restarting the run or duplicating content.

This is especially important for production agent applications. Long-running agents are not edge cases anymore; they are the workloads developers are building toward.

Multimodal Streams

The protocol is designed around content blocks rather than plain strings, which makes multimodal streaming a natural extension of the same model.


Each page subscribes only to the media it needs, rendering text, images, and audio as they become available.
In the cookbook's multimodal storybook demo, a graph generates a bedtime story, page images, audio narration, and video. The UI scopes media selectors to the graph nodes responsible for each page, so each page can render as soon as its assets arrive.

const visualizer = useNodeRun(`visualizer_${index}`);
const images = useImages(stream, visualizer?.namespace);
const imageURL = useMediaURL(images[0]);
The important part is not the demo itself. It is that text, reasoning, tool activity, images, audio, video, and custom data all fit into the same streaming architecture: typed blocks, named channels, namespaces, and projections.

Framework SDKs for Real Applications

The release also brings v1 framework packages for building streamed agent applications:

@langchain/react
@langchain/vue
@langchain/svelte
@langchain/angular
Each package exposes the same streaming concepts in the idioms of the framework. React uses hooks, Vue uses composables, Svelte uses reactive helpers, and Angular uses injectors and signals.

The core mental model is shared:

One root hook: useStream or injectStream in Angular
Top-level projections: messages, values, tool calls, interrupts, are available without setup.
Component-level selectors: useMessages, useToolCalls, useExtension, and friends for scoped subscriptions only when something mounts.
Subagents and subgraphs show up immediately: their detailed streams open only when you reach for them.
Remounting on the same thread reattaches to the in-flight run without replay or duplication.
In React, a basic streamed chat can stay small:

const stream = useStream({
  assistantId: "agent",
  apiUrl: "<http://localhost:2024>",
  threadId,
});
 
const messages = useMessages(stream);
And a subagent-aware component can subscribe only to the data it renders:

function SubagentCard({ stream, subagent }) {
  const messages = useMessages(stream, subagent);
  const toolCalls = useToolCalls(stream, subagent);
 
  return <AgentTrace messages={messages} toolCalls={toolCalls} />;
}
That is the difference between callback-heavy streaming and render-driven streaming. Components mount the projections they need; the SDK handles subscription lifetimes, reconnection, and assembly.