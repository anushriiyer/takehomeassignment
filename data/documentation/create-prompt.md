> ## Documentation Index
> Fetch the complete documentation index at: https://docs.langchain.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create a prompt

In the [LangSmith UI](https://smith.langchain.com?utm_source=docs\&utm_medium=cta\&utm_campaign=langsmith-signup\&utm_content=langsmith-create-a-prompt), navigate to the **Playground** in the left-hand sidebar or from the application homepage.

<img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/W4JD1iHHqOz2208Y/langsmith/images/empty-playground-light.png?fit=max&auto=format&n=W4JD1iHHqOz2208Y&q=85&s=786a59677dc324a56ace6047f9e842c7" alt="Empty playground" width="1436" height="529" data-path="langsmith/images/empty-playground-light.png" />

<img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/W4JD1iHHqOz2208Y/langsmith/images/empty-playground-dark.png?fit=max&auto=format&n=W4JD1iHHqOz2208Y&q=85&s=395803856f558538a1b6412b579ead74" alt="Empty playground" width="1436" height="521" data-path="langsmith/images/empty-playground-dark.png" />

## Compose your prompt

The left panel of the playground is an editable view of the prompt.

The prompt is made up of messages, each of which has a *role*, including:

* **System**: The "instruction manual". Use this to define the AI's persona, tone, and ground rules (e.g., "You are a helpful assistant that explains things like the weather").
* **Human**: The "user". This represents the person asking questions or providing instructions to the AI.
* **AI**: The "assistant". This is the model’s response. In the playground, you can use this to provide "few-shot" examples—showing the AI exactly how you want it to respond.
* **Tool / Function**: These roles represent the output from external tools (like a calculator or a search engine). They help you test how the AI should behave after receiving specific data.
* **Chat**: A general-purpose role, often used when importing logs or conversation history where specific labels haven't been assigned.
* **Messages List**: A dynamic placeholder. This allows you to add a variable that contains an entire list of previous messages, making it easy to manage long conversation histories.

### Template format

The default [template format](/langsmith/prompt-template-format) is f-string, but you can change the prompt template format to mustache by clicking on the dropbox below the prompt boxes.

### Add a template variable

Prompts become particularly useful when you add variables in your prompt. You can use variables to add dynamic content to your prompt. Add a template variable in one of two ways:

* Add `{variable_name}` to your prompt (with one curly brace on each side for f-string or two for mustache).

  <img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/IBetwXCjfWGXPKi_/langsmith/images/prompt-with-variable-light.png?fit=max&auto=format&n=IBetwXCjfWGXPKi_&q=85&s=82145f5811abf37c65895de427fedcd4" alt="Variable in prompt box." width="1616" height="584" data-path="langsmith/images/prompt-with-variable-light.png" />

  <img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/IBetwXCjfWGXPKi_/langsmith/images/prompt-with-variable-dark.png?fit=max&auto=format&n=IBetwXCjfWGXPKi_&q=85&s=fd59e4415c81a9c627206e0df182d261" alt="Variable in prompt box." width="1610" height="568" data-path="langsmith/images/prompt-with-variable-dark.png" />

* Highlight text you want to templatize and click **Convert to variable** tooltip button that displays. Enter a name for your variable, and convert.

  <img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/M4xkWV5X4-OcEJgy/langsmith/images/convert-to-variable-light.png?fit=max&auto=format&n=M4xkWV5X4-OcEJgy&q=85&s=a1c23d34cb194d5c63f0fcab575fc194" alt="Double clicking on a prompt displays the variable icon." width="1590" height="624" data-path="langsmith/images/convert-to-variable-light.png" />

  <img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/M4xkWV5X4-OcEJgy/langsmith/images/convert-to-variable-dark.png?fit=max&auto=format&n=M4xkWV5X4-OcEJgy&q=85&s=58922b751727b746fd9be5978c7666f7" alt="Double clicking on a prompt displays the variable icon." width="1562" height="634" data-path="langsmith/images/convert-to-variable-dark.png" />

Once you've added a variable, the right panel of the playground will have an **Input** box for a sample input for the prompt variable. Fill these in with values to test the prompt.

<Callout icon="book" color="#4F46E5" iconType="regular">
  For more details on the prompt template formats generally and examples in both syntax, refer to the [Prompt template format](/langsmith/prompt-template-format) guide.
</Callout>

### Structured output

Adding an output schema to your prompt will get output in a structured format. Learn more about [structured output](/langsmith/prompt-engineering-concepts#structured-output).

### Tools

You can also add a tool by clicking the **+ Tool** button at the bottom of the prompt editor. For more information on how to use tools, refer to [Use tools](/langsmith/use-tools).

<Callout type="info" icon="feather">
  Use the **[Polly](/langsmith/polly)** AI assistant in the Playground to generate tools, create output schemas, and optimize your prompts with AI assistance.
</Callout>

## Run the prompt

To run a prompt, use <Icon icon="player-play" /> **Start** at the top of the right panel in the playground.

## Save your prompt

To save your prompt, click the **Save** button and name your prompt.

The model and configuration you select in the playground settings will be saved with the prompt. When you reopen the prompt, the model and configuration will automatically load from the saved version.

<Check>
  The first time you create a public prompt, you'll be asked to set a LangChain Hub handle. All your public prompts will be linked to this handle. In a shared workspace, this handle will be set for the whole workspace.
</Check>

## View your prompts

After you've created a prompt, you can view a table of your prompts under **Prompts** in the left-hand side bar.

## Add metadata

To add metadata to your prompt, click the <Icon icon="dots-vertical" /> **More** icon on the top right-hand side of the page and then click the <Icon icon="pencil" /> **Update metadata** from the dropdown. This brings you to a page where you can add additional information about the prompt, including a description and README.

# Next steps

Now that you've created a prompt, you can use it in your application code. See [how to pull a prompt programmatically](/langsmith/manage-prompts-programmatically#pull-a-prompt).

***

<div className="source-links">
  <Callout icon="terminal-2">
    [Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.
  </Callout>

  <Callout icon="edit">
    [Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/langsmith/create-a-prompt.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).
  </Callout>
</div>