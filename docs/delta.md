# The delta signal

## The claim

The training signal is the **delta between two locally-cached
models on the same task**, filtered by the **same predicate the
compiler uses to emit**. Both models on disk. No network. No
third-party teacher. The pipeline generates its own harder
training set by contrasting what one model can do and another
cannot.

## The four quadrants

|                | A passes       | A fails          |
|----------------|----------------|------------------|
| **B passes**   | both_pass      | B_beats_A        |
| **B fails**    | A_beats_B      | both_fail        |

Only off-diagonal quadrants emit training pairs. Diagonals are
routing decisions:

- both_pass   -> discard; the task is below the student's level
- both_fail   -> escalate; the task is above both models' level

## The filter

`filter_delta` re-runs the workload's verifier on both outputs.
The verifier is the same object the emitter uses. If the teacher
no longer passes or the student unexpectedly passes, the pair is
rejected.

## The output

Two formats, one line per pair:

- SFT: `(prompt, completion)` where completion is teacher output
- DPO: `(prompt, chosen, rejected)` where chosen=teacher,
  rejected=student

Both are appended to `.delta/`. A downstream offline trainer
consumes them. The pipeline emits; it does not train.

## The honest limits

1. The pipeline does not fine-tune. It emits the signal.
2. If both models are identical checkpoints, the signal is zero.
   Diversity between the two models is required for signal to
   exist at all.
3. If model A is orders of magnitude stronger, all deltas are
   A_beats_B. To drive both, roles must be swapped and re-run
   after offline fine-tuning.
4. The verifier must be sound. A weak verifier produces a
   curriculum that is honest and useless. The predicate is the
   ceiling of the signal.
5. Both-on-diagonal quadrants produce no training pair. The
   pipeline names them and moves on. That naming is the whole
   point: it is what keeps the signal clean.
