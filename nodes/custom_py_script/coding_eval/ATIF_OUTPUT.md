# minisweBenchmark output contract

`minisweBenchmark.yaml` declares one output, `output_file_path` (`STRING`). For one benchmark task with a valid trace, its value is the path to a JSON file containing **one complete ATIF-v1.8 trajectory object**. If that task has no valid trace, the output points to a manifest describing the failure. The native `preds.json` produced by `mini-extra swebench` does not satisfy this contract.

The contract follows the [Harbor ATIF specification](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md). The required root fields are `schema_version`, `agent`, and `steps`. Set `schema_version` to `ATIF-v1.8`; include `session_id` and `trajectory_id` for traceability. The `agent` object needs `name` and `version`. Each step needs a sequential `step_id` starting at 1, `source` (`system`, `user`, or `agent`), and `message`. Record tool calls and their observations in the corresponding agent steps when they occur.

ATIF has no dedicated benchmark-score field. Put task identity and verifier results in `final_metrics.extra`, alongside standard token totals in `final_metrics` when they are available. Do not invent missing model usage or tool events.

Example shape (illustrative, not an output of the current scaffold):

```json
{
  "schema_version": "ATIF-v1.8",
  "session_id": "benchmark-run-001",
  "trajectory_id": "benchmark-task-001",
  "agent": {
    "name": "benchmark-agent",
    "version": "1.0.0",
    "model_name": "served-model"
  },
  "steps": [
    {"step_id": 1, "source": "user", "message": "Task instructions"},
    {"step_id": 2, "source": "agent", "message": "Agent response"}
  ],
  "final_metrics": {
    "total_steps": 2,
    "extra": {
      "benchmark": {
        "name": "benchmark-name",
        "task_id": "task-001",
        "score": 1.0
      }
    }
  }
}
```

A multi-task run writes one independent ATIF-v1.8 document per task, never an
array disguised as one ATIF trajectory. For more than one task,
`output_file_path` points to `manifest.json` with
`schema_version: "EvalBenchmarkManifest-v1"`. This index is **not an ATIF
document**; `tasks[].output_file_path` references each validated ATIF file.
The index records task IDs, per-task scores, resolved counts and the mean
score. All task trajectories share a run/session ID and have distinct
`trajectory_id` values and their own step numbering starting at one.

For one task with a valid trace, `output_file_path` points directly to
`trajectory.atif.json`, even if grading failed; its benchmark then records the
failure with a null score. Without a valid trace, the output is `manifest.json`.
The number of attempted tasks determines the output shape, including tasks
whose inference failed before saving a prediction. Missing or invalid traces
have a null `tasks[].output_file_path`; no ATIF events are synthesized.

## Implemented export

`eval_benchmark.py` launches `run_swebench.py`, which uses mini-swe-agent's
existing SWE-bench inference entry point and submits each completed task to an
independent grading pool. `rollout_config.inference_workers` limits agent
concurrency; `grading_workers` limits concurrent SWE-bench 5.0.2 verifiers.
Each task's trace is validated before that task is graded. Online grading
reports and logs live under `verified/<task_id>/`; native traces stay under `runs/`.
Harness summaries are named `summary.json`; task reports and test logs are
flattened into that same directory after grading, including failed attempts.
Existing historical runs are not moved. Each task's Agent and
verifier IDs are recorded under `sandbox-containers/<task_id>/`. As soon as that
task's grading finishes, including unresolved results or grading errors, its
recorded containers are removed without affecting other tasks. Cleanup failures
retain their records for a final retry. Trajectories and reports are preserved.
Both pools finish before final cleanup and daemon shutdown. Per-task callback,
trajectory and grading exceptions are collected rather than aborting final
export. A native trajectory's `info.exception_str` also identifies an inference
failure that mini-swe-agent caught internally. Valid traces remain exportable
when grading fails; invalid or absent traces retain only their original files
and the manifest failure entry. Dataset-loading failures and output I/O errors
still fail the batch, and interrupts are not converted into task results.
Final export runs
after all results are available and returns
`output_dir/eval-<uuid>/trajectory.atif.json`. Each file is validated with Harbor
0.25.0's `Trajectory` model and uses exactly `ATIF-v1.8`.
For multiple tasks the files instead live under
`output_dir/eval-<uuid>/trajectories/<task_id>.atif.json`; the manifest stays at the run root.

The exporter reads `runs/<instance_id>/<instance_id>.traj.json`. Assistant tool
calls retain their native IDs; tool results are associated by ID, including
parallel calls whose results arrive out of order. Native exit records become
system steps marked with `extra.native_role = "exit"`. Tool return codes are
kept in observation-result metadata. Export currently supports the launcher's
saved text/chat-completions format; unknown roles and unsupported non-text
content are rejected rather than silently removed.

Only recorded usage is exported. Aggregate usage is omitted when any agent
step lacks that metric. Zero costs from `ignore_errors` are omitted because
they can indicate an unknown price. Task success comes from harness results,
not the agent's exit status; missing/error/infra-failure reports are errors.
Ordinary unresolved tasks and empty patches produce a real score of zero.
Before grading, whitespace-only patches are normalized to empty strings in a
separate harness prediction file (`verified/<task_id>/preds.harness.json` for
online runs, `verified/preds.harness.json` for offline batch grading); native predictions and nonempty diffs
are preserved. These tasks receive the harness's ordinary empty-patch score.

`atif_export.py` also provides an offline CLI for converting saved artifacts.
Without a normalized grading result, it marks grading as `not_run` and omits
the score. Local offline validation does not establish
real inference or verifier execution; see `nodes/README.md` for commands and
the remaining Pod/region validation requirements.

`finish_evaluation.py` joins grading/report replay with ATIF export without
invoking inference. It validates the native trace before starting any verifier.
For multiple predictions every trace is validated before invoking the verifier
once with all selected task IDs and bounded worker concurrency.
Report replay requires the original harness run ID and accepts the new online
`verified/` directory with per-task `summary.json` and `report.json`, older per-task
online report directories, batch report directories, and PyroDash-flattened reports.
A compact `benchmark.json` always contains
`summary` (`total_tasks`, `scored_tasks`, `failed_tasks`, `resolved_tasks`,
`mean_score`), a task-ID-keyed `tasks` object whose values contain only `status`,
`resolved`, and `score`, and a separate `failed_tasks` object mapping task IDs
to `stage` and `error`. Failed tasks use `status: "failed"`, null `resolved`
and null `score`. The mean includes only completed scores, including ordinary
zero scores. If all tasks fail, `scored_tasks` is zero and `mean_score` is null;
the summary and failure list are still exported. Manifests carry the same
summary and failure details. With no failures, the count is zero and the
failure object is empty.
This shape is the same for one or multiple tasks. Explicit Docker grading first checks the supplied daemon;
it never starts a daemon implicitly. Synthetic reports remain synthetic even
when their structure passes the same validators as real reports.

`atif_export.py --task-id <id>` can export one task from a batch prediction
file. With a multi-task `benchmark.json`, the same flag selects that task's
normalized grading result. The standalone `finish_evaluation.py` and
`atif_export.py` entry points retain their strict validation: missing/invalid
traces or incomplete grading reports raise errors. Per-task failure collection
is implemented in the online `run_swebench.py` pipeline. Ordinary unresolved
tasks are valid results with score zero.
