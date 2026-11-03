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

- [x] Choose SWE-bench Verified (`--slice 0:1`) for prediction and `SWE-bench/SWE-bench_Verified` for the 5.0.2 verifier. The dataset is fetched by the tools, not bundled here.
- [ ] Confirm that benchmark sandboxes can reach the endpoint and that the supplied model ID is served there.
- [ ] Confirm the Pod can install the Docker CLI, start docker-rt, access benchmark images, and import the evaluator's Python dependencies.
- [x] Implement a verifier invocation and capture its score and per-task results; live execution is still unverified.
- [x] Convert saved chat-completions user, agent, tool, and observation events into ATIF-v1.8 steps; place verifier results in `final_metrics.extra`.
- [x] Validate against Harbor 0.25.0's ATIF reference models and return the ATIF file path as `output_file_path`.
- [x] Verify conversion, result handling and node orchestration with synthetic artifacts and mocked inference/verifier/Docker calls.
- [ ] For a multi-task benchmark, write one ATIF document per task and decide how the workflow should expose the collection of artifacts.
- [x] Use unique output directories, preserve failure artifacts, reject incomplete/infra-error grading, and set a verifier subprocess timeout.
- [ ] Validate Docker resource cleanup, shared socket behavior, and regional docker-rt compatibility in a real Pod.
- [ ] Verify one-task execution end to end, then expand to the full benchmark.

The node entry retains the existing prediction call, invokes the verifier, then
returns a validated `trajectory.atif.json`. The original `preds.json` and
`<instance_id>/<instance_id>.traj.json` remain as intermediate artifacts. Current
conversion supports the saved text/chat-completions trace used by the existing
launcher; unsupported message roles or non-text content fail explicitly. No
real model inference, Docker startup, benchmark grading, or deployment was used
for offline validation. Pinning dependencies does not establish live Pod compatibility.
