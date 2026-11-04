# EvalBenchmark checklist

## Done

- [x] Remove the copied offload routing and adapter helpers.
- [x] Rename the custom node to `EvalBenchmark`.
- [x] Accept an existing HTTP(S) model endpoint as the node input.
- [x] Make endpoint optional in the node form; accept a connected Inference output and report a missing runtime address before allocating sandboxes.
- [x] Accept the served model name and API key as node inputs.
- [x] Prepare a Docker CLI and start docker-rt with a separate PyroMind API key, cluster, and log file before prediction.
- [x] Define `output_file_path` as a path to an ATIF-v1.8 trajectory JSON file; see `ATIF_OUTPUT.md`.
- [x] Add a Python `subprocess` launcher for the SWE-bench Verified prediction phase.
- [x] Call the prediction launcher from the `eval_benchmark` node entry.
- [x] Use the supplied endpoint without starting a model server or offload adapter.
- [x] Default to one SWE-bench Verified task; allow `num_tasks` and `start_index` to select a batch.

## Remaining

- [x] Choose SWE-bench Verified for prediction and `SWE-bench/SWE-bench_Verified` for the 5.0.2 verifier. The dataset is fetched by the tools, not bundled here.
- [ ] Confirm that benchmark sandboxes can reach the endpoint and that the supplied model ID is served there.
- [ ] Confirm the Pod can install the Docker CLI, start docker-rt, access benchmark images, and import the evaluator's Python dependencies.
- [x] Implement a verifier invocation and capture its score and per-task results; live execution is still unverified.
- [x] Convert saved chat-completions user, agent, tool, and observation events into ATIF-v1.8 steps; place verifier results in `final_metrics.extra`.
- [x] Validate against Harbor 0.25.0's ATIF reference models and return the ATIF file path as `output_file_path`.
- [x] Verify conversion, result handling and node orchestration with synthetic artifacts and mocked inference/verifier/Docker calls.
- [x] For multiple tasks, run the verifier once, write one validated ATIF per task and expose their paths/scores through `manifest.json`; preserve direct ATIF output for one task.
- [x] Verify multi-task selection, concurrency, task/report association, aggregate scores, and failure handling with synthetic artifacts and mocked calls.
- [x] Include LiteLLM's MCP extra and validate its actual tool-calling import path before sandbox creation; verify Mini SWE Agent tool-call parsing with LiteLLM's built-in mock response.
- [x] Require model_name in the node form and rely on platform required-field validation; keep required YAML parameters before optional parameters.
- [x] Use the supplied model ID directly for inference and ATIF metadata without requesting `/models`, discovering models, or rewriting aliases.
- [x] Make the model endpoint API key optional for unauthenticated services; omit metadata auth when empty and use an inert client placeholder rather than inheriting real credentials. Keep the platform API key required.
- [x] Use unique output directories, preserve failure artifacts, reject incomplete/infra-error grading, and set a verifier subprocess timeout.
- [x] Add an inference-free CLI to grade saved predictions or replay existing harness reports, including PyroDash's flattened layout.
- [x] Require SDK 0.1.15 and check the actual docker-rt CLI capabilities; install and verify Docker CLI 27.5.1 locally.
- [x] Use private sockets, PID files and Docker configs; stop the owned daemon in finally and attempt scoped verifier-container cleanup on failure/timeout.
- [ ] Validate remote sandbox cleanup and daemon behavior in a real Pod. Regional compatibility is outside the current scope.
- [ ] Verify one-task execution end to end, then expand to the full benchmark.

The node entry retains the existing prediction call, invokes the verifier, then
returns a validated `trajectory.atif.json`. The original `preds.json` and
`<instance_id>/<instance_id>.traj.json` remain as intermediate artifacts. Current
conversion supports the saved text/chat-completions trace used by the existing
launcher; unsupported message roles or non-text content fail explicitly. No
real model inference, Docker startup, benchmark grading, or deployment was used
for offline validation. Pinning dependencies does not establish live Pod compatibility.

The current workspace has Python 3.12.11, SDK 0.1.15 and a working Docker CLI.
A real node attempt downloaded the 500-task Verified dataset and started the
benchmark container, but failed before producing a model response because the
MCP dependency was missing. The dependency fix is locally validated with a
mocked tool response. Successful real prediction, scoring and full workflow
execution remain unverified; report replay is not a live score.
