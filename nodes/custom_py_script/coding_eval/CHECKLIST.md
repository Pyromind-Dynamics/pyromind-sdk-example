# EvalBenchmark checklist

## Done

- [x] Remove the copied offload routing and adapter helpers.
- [x] Rename the custom node to `EvalBenchmark`.
- [x] Accept an existing HTTP(S) model endpoint as the node input.
- [x] Accept the served model name and API key as node inputs.
- [x] Prepare a Docker CLI and start docker-rt with a separate PyroMind API key, cluster, and log file before prediction.
- [x] Define `output_file_path` as a path to an ATIF-v1.8 trajectory JSON file; see `ATIF_OUTPUT.md`.
- [x] Add a Python `subprocess` launcher for the SWE-bench Verified prediction phase.
- [x] Call the prediction launcher from the `eval_benchmark` node entry.
- [x] Use the supplied endpoint without starting a model server or offload adapter.
- [x] Limit the node entry to one SWE-bench Verified task with `--slice 0:1`.

## Remaining

- [ ] Choose the first benchmark and define how its dataset or task set is provided to the node. No coding benchmark dataset is bundled here.
- [ ] Confirm that benchmark sandboxes can reach the endpoint and that the supplied model ID is served there.
- [ ] Confirm the Pod can install the Docker CLI, start docker-rt, access benchmark images, and import the evaluator's Python dependencies.
- [ ] Run the benchmark verifier and capture its score and per-task results.
- [ ] Convert the actual user, agent, tool, and observation events into ATIF-v1.8 steps; place verifier results in `final_metrics.extra`.
- [ ] Validate each trajectory against Harbor's ATIF reference models and return its file path as `output_file_path`.
- [ ] For a multi-task benchmark, write one ATIF document per task and decide how the workflow should expose the collection of artifacts.
- [ ] Handle run failure, timeouts, cleanup, and unique output directories.
- [ ] Verify one-task execution end to end, then expand to the full benchmark.

The node entry currently returns the path to MiniSweAgent's native `preds.json`. Grading and ATIF generation are still pending, so this intermediate output does not yet satisfy the ATIF output contract.
