> ## Documentation Index
> Fetch the complete documentation index at: https://docs.langchain.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Analyze an experiment

This page describes some of the essential tasks for working with [*experiments*](/langsmith/evaluation-concepts#experiment) in LangSmith:

* **[Analyze a single experiment](#analyze-a-single-experiment)**: View and interpret experiment results, customize columns, filter data, and compare runs.
* **[Set a baseline in the Experiments tab view](#set-a-baseline-in-the-experiments-tab-view)**: Set a baseline for a dataset that you want to outperform.
* **[Filter and group by models, prompts, and tools in the Experiments tab view](#filter-and-group-by-models-prompts-and-tools-in-the-experiments-tab-view)**: Use **Models**, **Prompts**, and **Tools** columns to filter and group experiments in the **Experiments** tab view.
* **[Download experiment results as a CSV](#download-experiment-results-as-a-csv)**: Export your experiment data for external analysis and sharing.
* **[Rename an experiment](#rename-an-experiment)**: Update experiment names in both the Playground and experiment view.

## Analyze a single experiment

After running an experiment, you can use LangSmith's experiment view to analyze the results and draw insights about your experiment's performance.

### Open the experiment view

To open the experiment view,

1. Select the relevant [*dataset*](/langsmith/evaluation-concepts#datasets) from the **Dataset & Experiments** page which opens the **Experiments** tab view.
2. Click the row of the experiment you want to view.

<img src="https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/select-experiment.png?fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=74207f0a2422f89fdc75b23f0a88c58f" alt="Open experiment view" width="1640" height="899" data-path="langsmith/images/select-experiment.png" />

### View experiment results

#### Customize columns

By default, the experiment view shows the input, output, and reference output for each [example](/langsmith/evaluation-concepts#examples) in the dataset, feedback scores from evaluations and experiment metrics like cost, token counts, latency and status.

You can customize the columns clicking the **Columns** icon at the top right of the view to make it easier to interpret experiment results:

* **Break out fields from inputs, outputs, and reference outputs** into their own columns. This is especially helpful if you have long inputs/outputs/reference outputs and want to surface important fields.
* **Hide and reorder columns** to create focused views for analysis.
* **Control decimal precision on feedback scores**. By default, LangSmith surfaces numerical feedback scores with a decimal precision of 2, but you can customize this setting to be up to 6 decimals.
* **Set the Heat Map threshold** to high, middle, and low for numeric feedback scores in your experiment, which affects the threshold at which score chips render as red or green:

<img src="https://mintcdn.com/langchain-5e9cc07a/aKRoUGXX6ygp4DlC/langsmith/images/column-heat-map.png?fit=max&auto=format&n=aKRoUGXX6ygp4DlC&q=85&s=b0203a449f0f7df70900735ba540d712" alt="Column heatmap configuration" width="1780" height="1688" data-path="langsmith/images/column-heat-map.png" />

<Tip>
  You can set default configurations for an entire dataset or temporarily save settings just for yourself.
</Tip>

#### Sort and filter

To sort rows by a feedback score, click the **Sort by** icon in the column header.

<img src="https://mintcdn.com/langchain-5e9cc07a/Tdk8epB4BZgbugRX/langsmith/images/column-sort.png?fit=max&auto=format&n=Tdk8epB4BZgbugRX&q=85&s=19a77a5df00a579f3bd953fd75c4ade9" alt="Sort column" width="1578" height="461" data-path="langsmith/images/column-sort.png" />

To filter rows, click the <Icon icon="dots-vertical" /> icon in the column header and configure your filter settings.

<img src="https://mintcdn.com/langchain-5e9cc07a/Tdk8epB4BZgbugRX/langsmith/images/column-filter.png?fit=max&auto=format&n=Tdk8epB4BZgbugRX&q=85&s=d76a7c51f386c511679ad84ad6ca4d86" alt="Filter column" width="1578" height="461" data-path="langsmith/images/column-filter.png" />

#### Table views

Select one of three table view icons at the top right of the experiment view:

* **Compact**: Shows each run as a single row for quick score comparisons.
* **Full**: Shows the full output for each run.
* **Diff**: Shows the text difference between the reference output and the output for each run.

<img src="https://mintcdn.com/langchain-5e9cc07a/Tdk8epB4BZgbugRX/langsmith/images/diff-mode.png?fit=max&auto=format&n=Tdk8epB4BZgbugRX&q=85&s=800ecac6a9fc6d8ef426a41999c65a44" alt="Diff view" width="1235" height="468" data-path="langsmith/images/diff-mode.png" />

#### View the traces

Click any row in the experiment view to open the details panel, which shows the trace alongside feedback, input, output, and attributes for that run.

<img src="https://mintcdn.com/langchain-5e9cc07a/Tdk8epB4BZgbugRX/langsmith/images/view-trace.png?fit=max&auto=format&n=Tdk8epB4BZgbugRX&q=85&s=f39235b29c4fca4bcb3cf4d4788133ca" alt="View trace" width="1583" height="842" data-path="langsmith/images/view-trace.png" />

To view the entire tracing project, click on the **View Project** icon at the top right of the experiment view.

#### View evaluator runs

By hovering over the evaluator score, you can view additional details about that evaluator run. For [LLM-as-a-judge evaluators](/langsmith/llm-as-judge), click the **Source** link to view the prompt used, or **Evaluator trace** to open the trace in a new browser tab. For experiments with [repetitions](/langsmith/repetition), click the aggregate average score to view links to all individual runs.

<img src="https://mintcdn.com/langchain-5e9cc07a/Tdk8epB4BZgbugRX/langsmith/images/evaluator-run.png?fit=max&auto=format&n=Tdk8epB4BZgbugRX&q=85&s=372dc06ba8bdb552b6afbdce0de1dee7" alt="View evaluator runs" width="889" height="528" data-path="langsmith/images/evaluator-run.png" />

### Group results by metadata

You can add metadata to examples to categorize and organize them. For example, if you're evaluating factual accuracy on a question answering dataset, the metadata might include which subject area each question belongs to. Metadata can be added either [via the UI](/langsmith/manage-datasets-in-application#edit-example-metadata) or [via the SDK](/langsmith/manage-datasets-programmatically#update-single-example).

To analyze results by metadata, use the **Group by** icon at the top right of the experiment view and select your desired metadata key. This displays average feedback scores, latency, total tokens, and cost for each metadata group.

<Info>
  You will only be able to group by example metadata on experiments created after February 20th, 2025. Any experiments before that date can still be grouped by metadata, but only if the metadata is on the experiment traces themselves.
</Info>

### Repetitions

If you've run your experiment with [*repetitions*](/langsmith/repetition), click any row to open the details panel. The **Repetition Summary** shows a metrics table, all feedback scores, and lets you toggle through outputs or view individual repetitions with their traces.

<img src="https://mintcdn.com/langchain-5e9cc07a/Tdk8epB4BZgbugRX/langsmith/images/repetitions.png?fit=max&auto=format&n=Tdk8epB4BZgbugRX&q=85&s=15a7c9c1a20042fbcdf1d5f7adcc25de" alt="Repetitions" width="1592" height="922" data-path="langsmith/images/repetitions.png" />

### Compare to another experiment

In the top right of the experiment view, you can select another experiment to compare to. This will open up a comparison view, where you can see how the two experiments compare. To learn more about the comparison view, see [how to compare experiment results](/langsmith/compare-experiment-results).

## Set a baseline in the Experiments tab view

While you may run dozens of tests, you typically have a specific benchmark you are trying to outperform. Setting a *baseline* anchors your results against this reference point, which allows you to identify improvements or regressions in a crowded experiment list.

By designating a baseline, you can:

* Highlight a reference: Explicitly mark your best-performing run so it remains visible at the top of the **Experiments** tab view as you iterate.
* See instant diffs: View performance deltas across all experiments automatically, which means you don't necessarily need to perform manual side-by-side selection.
* Accelerate assessment: Quickly determine if new iterations meet or exceed your current performance standards.

<img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/IYnogEjgWaxIU1jM/langsmith/images/baseline-experiment-view-light.png?fit=max&auto=format&n=IYnogEjgWaxIU1jM&q=85&s=3d192616f7373ce0f7c5996a6c65cc5e" alt="The Experiments tab view with an experiment marked as the baseline at the top of the table. Scores show against the baseline on the rows of other experiments." width="3200" height="714" data-path="langsmith/images/baseline-experiment-view-light.png" />

<img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/PSSTIduMbnDkYvaS/langsmith/images/baseline-experiment-view-dark.png?fit=max&auto=format&n=PSSTIduMbnDkYvaS&q=85&s=fba425d88cce62f2948cf3e1e47582cc" alt="The Experiments tab view with an experiment marked as the baseline at the top of the table. Scores show against the baseline on the rows of other experiments." width="3202" height="760" data-path="langsmith/images/baseline-experiment-view-dark.png" />

To set a baseline for a dataset:

1. In the [LangSmith UI](https://smith.langchain.com?utm_source=docs\&utm_medium=cta\&utm_campaign=langsmith-signup\&utm_content=langsmith-analyze-an-experiment), navigate to the **Datasets & Experiments** option in the left menu.
2. Select the dataset that you want to work with from the table.
3. In the **Experiments** tab view, hover over an experiment row to display the **Set baseline** button on the right end of the row. Click to select your baseline experiment.

Your baseline experiment will pin to the top of the table and have the **Baseline** tag next to its name. Once an experiment is set as a baseline, the table will display scores against the baseline on each experiment for each column. When you are selecting multiple experiments for comparison, the baseline experiment will be the default source experiment to be compared to.

## Filter and group by models, prompts, and tools in the Experiments tab view

The experiments table includes **Models**, **Prompts**, and **Tools** columns that show which models, prompts, and tools were used for each experiment, making it easier to understand what changed between runs at a glance.

These columns are populated automatically when you run experiments from the Playground. When running experiments via the SDK, pass a `metadata` object with `models`, `prompts`, and `tools` keys to `evaluate()`:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
results = client.evaluate(
    target,
    data="my-dataset",
    evaluators=[...],
    metadata={
        "models": "openai:gpt-5.4-mini",
        "prompts": ["my-org/my-prompt:abc12345"],
        "tools": [{"name": "web_search", "description": "Search the web for information"}],
    },
)
```

See [how to evaluate an LLM application](/langsmith/evaluate-llm-application#run-the-evaluation) for an example using metadata.

The columns only appear when at least one experiment in the dataset has the field set. Once populated, click on a value in these columns to filter or group experiments.

<img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/4y4TUahoyWs6oiHd/langsmith/images/metadata-columns-light.png?fit=max&auto=format&n=4y4TUahoyWs6oiHd&q=85&s=c08271466c5a6b923c1132b6edbb21c8" alt="The Experiments tab view with metadata columns for models, prompts, and tools." width="1293" height="296" data-path="langsmith/images/metadata-columns-light.png" />

<img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/4y4TUahoyWs6oiHd/langsmith/images/metadata-columns-dark.png?fit=max&auto=format&n=4y4TUahoyWs6oiHd&q=85&s=7706671f545f24691e7cd8bdf419f7e0" alt="The Experiments tab view with metadata columns for models, prompts, and tools." width="1284" height="287" data-path="langsmith/images/metadata-columns-dark.png" />

You can also filter and group by models, model providers, prompts, prompt commits, tools, and other experiment metadata at the top left of the **Experiments** tab view:

<img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/4y4TUahoyWs6oiHd/langsmith/images/metadata-group-by-light.png?fit=max&auto=format&n=4y4TUahoyWs6oiHd&q=85&s=4240516c40a0673a458786727df3f68d" alt="The Experiments tab view with metadata columns for models, prompts, and tools." width="1015" height="553" data-path="langsmith/images/metadata-group-by-light.png" />

<img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/4y4TUahoyWs6oiHd/langsmith/images/metadata-group-by-dark.png?fit=max&auto=format&n=4y4TUahoyWs6oiHd&q=85&s=2d32c89b32f083c50cae746888fdbc83" alt="The Experiments tab view with metadata columns for models, prompts, and tools." width="1006" height="573" data-path="langsmith/images/metadata-group-by-dark.png" />

## Download experiment results as a CSV

LangSmith lets you download experiment results as a CSV file for external analysis and sharing. Click the **Download as CSV** icon at the top right of the experiment view.

<Note>
  There is a 5,000 row download limit for experiment results.
</Note>

## Rename an experiment

<Note>
  Experiment names must be unique per workspace.
</Note>

You can rename an experiment in the LangSmith UI in the following places:

* **Experiment view**: Rename an experiment by using the pencil icon beside the experiment name.

  <img src="https://mintcdn.com/langchain-5e9cc07a/4y4TUahoyWs6oiHd/langsmith/images/rename-in-experiment-view.png?fit=max&auto=format&n=4y4TUahoyWs6oiHd&q=85&s=9361c74c51c2e109f7bfd877959eb015" alt="Edit name in experiment view" width="1188" height="148" data-path="langsmith/images/rename-in-experiment-view.png" />

* **Playground**: A default name with the format `pg::prompt-name::model::uuid` (eg. `pg::gpt-5.4-mini::897ee630`) is automatically assigned. You can rename an experiment immediately after running it by editing its name in the Playground table header.

  <img src="https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/rename-in-playground.png?fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=5b647ff1894376bbb727dabc4d73f039" alt="Edit name in playground" width="1372" height="200" data-path="langsmith/images/rename-in-playground.png" />

***

<div className="source-links">
  <Callout icon="terminal-2">
    [Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.
  </Callout>

  <Callout icon="edit">
    [Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/langsmith/analyze-an-experiment.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).
  </Callout>
</div>