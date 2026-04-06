## Clearing Database:
```  
  psql "$DATABASE_URL" -c "
  DELETE FROM chat.message_feedback
  WHERE message_id IN (
    SELECT id
    FROM chat.messages
    WHERE student_id LIKE 'fixture_%'
  );

  DELETE FROM chat.messages
  WHERE student_id LIKE 'fixture_%';

  DELETE FROM current_state.state_snapshots
  WHERE student_id LIKE 'fixture_%';

  DELETE FROM event_logs.parsed_events
  WHERE student_id LIKE 'fixture_%';
  "
```

## Inserting Logs:
```
  for f in tests/fixtures/raw_logs/*.ndjson; do
    python3 src/parse_event_logs.py --input "$f" --insert
  done
```

## Input Fields on UI
- StudentID
- "GO-Mars"
- SessionID

## Fixtures:

1.1 `01_error_flagging_a.ndjson`
- StudentID: `fixture_01_1`
- SessionID: `20000000-0000-0000-0001-000000000001`
- Intended analyzer cognition: `LONG_TERM_STALLED_PROGRESS`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Error Flagging}`
- Meaning: disconnected drive block, no progress, repeated unsuccessful runs

1.2 `01_error_flagging_b.ndjson`
- StudentID: `fixture_01_2`
- SessionID: `20000000-0000-0000-0001-000000000002`
- Intended analyzer cognition: `LONG_TERM_STALLED_PROGRESS`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Error Flagging}`
- Meaning: disconnected turn block, long stalled session with no scoring progress

1.3 `01_error_flagging_c.ndjson`
- StudentID: `fixture_01_3`
- SessionID: `20000000-0000-0000-0001-000000000003`
- Intended analyzer cognition: `LONG_TERM_STALLED_PROGRESS`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Error Flagging}`
- Meaning: connected drive plus orphaned arm block, so the scoring action never executes

2.1 `02_elaborate_a.ndjson`
- StudentID: `fixture_02_1`
- SessionID: `20000000-0000-0000-0002-000000000001`
- Intended analyzer cognition: `DEVELOPMENT_INCREASES_PROGRESS`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Elaborate}`
- Meaning: the student steadily improves a drive-path solution and accumulates progress through repeated successful runs

2.2 `02_elaborate_b.ndjson`
- StudentID: `fixture_02_2`
- SessionID: `20000000-0000-0000-0002-000000000002`
- Intended analyzer cognition: `DEVELOPMENT_INCREASES_PROGRESS`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Elaborate}`
- Meaning: the student reaches progress by reordering actions, so the improvement comes from sequencing rather than just adding more code

2.3 `02_elaborate_c.ndjson`
- StudentID: `fixture_02_3`
- SessionID: `20000000-0000-0000-0002-000000000003`
- Intended analyzer cognition: `DEVELOPMENT_INCREASES_PROGRESS`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Elaborate}`
- Meaning: the student progresses by solving a different subset of GO-Mars goals, not the same milestone path as the other Elaborate scenarios

3.1 `03_reassure_a.ndjson`
- StudentID: `fixture_03_1`
- SessionID: `20000000-0000-0000-0003-000000000001`
- Intended analyzer cognition: `DEVELOPMENT_STATIC_PROGRESS`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Reassure}`
- Meaning: the student keeps tweaking only drive distance values, but the robot never meaningfully improves

3.2 `03_reassure_b.ndjson`
- StudentID: `fixture_03_2`
- SessionID: `20000000-0000-0000-0003-000000000002`
- Intended analyzer cognition: `DEVELOPMENT_STATIC_PROGRESS`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Reassure}`
- Meaning: the student is stuck tuning heading and turn angles without unlocking any new task progress

3.3 `03_reassure_c.ndjson`
- StudentID: `fixture_03_3`
- SessionID: `20000000-0000-0000-0003-000000000003`
- Intended analyzer cognition: `DEVELOPMENT_STATIC_PROGRESS`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Reassure}`
- Meaning: the student mixes small drive and turn edits, but the overall program state stays flat the whole time

4.1 `04_inform_a.ndjson`
- StudentID: `fixture_04_1`
- SessionID: `20000000-0000-0000-0004-000000000001`
- Intended analyzer cognition: `DEVELOPMENT_DECREASES_PROGRESS`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Inform}`
- Meaning: progress falls because the student removes an arm-based scoring action that previously worked

4.2 `04_inform_b.ndjson`
- StudentID: `fixture_04_2`
- SessionID: `20000000-0000-0000-0004-000000000002`
- Intended analyzer cognition: `DEVELOPMENT_DECREASES_PROGRESS`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Inform}`
- Meaning: progress falls because the student breaks the navigation sequence, not because of arm control

4.3 `04_inform_c.ndjson`
- StudentID: `fixture_04_3`
- SessionID: `20000000-0000-0000-0004-000000000003`
- Intended analyzer cognition: `SNAP_N_TEST`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Inform}`
- Meaning: the student experiments by snapping a block into a loop structure, unsnapping it, and testing immediately to compare behavior

5.1 `05_partial_correctness_a.ndjson`
- StudentID: `fixture_05_1`
- SessionID: `20000000-0000-0000-0005-000000000001`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Partial Correctness}`
- Meaning: the student keeps changing drive-path values and alternates between partial success and total misses

5.2 `05_partial_correctness_b.ndjson`
- StudentID: `fixture_05_2`
- SessionID: `20000000-0000-0000-0005-000000000002`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Partial Correctness}`
- Meaning: the student repeatedly reworks turning behavior, producing recoveries after each setback

5.3 `05_partial_correctness_c.ndjson`
- StudentID: `fixture_05_3`
- SessionID: `20000000-0000-0000-0005-000000000003`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `IN_PROGRESS`
- Intended feedback class(es): `{Partial Correctness}`
- Meaning: the student alternates between motion and arm changes, so different subsystems cause the up-and-down progress pattern

6.1 `06_partial_correctness_evidence_based_praise_a.ndjson`
- StudentID: `fixture_06_1`
- SessionID: `20000000-0000-0000-0006-000000000001`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Partial Correctness, Evidence-based Praise}`
- Meaning: noisy experimentation eventually converges on a mostly successful path solution

6.2 `06_partial_correctness_evidence_based_praise_b.ndjson`
- StudentID: `fixture_06_2`
- SessionID: `20000000-0000-0000-0006-000000000002`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Partial Correctness, Evidence-based Praise}`
- Meaning: the student reaches likely completion mainly by correcting action order and timing after several failed runs

6.3 `06_partial_correctness_evidence_based_praise_c.ndjson`
- StudentID: `fixture_06_3`
- SessionID: `20000000-0000-0000-0006-000000000003`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Partial Correctness, Evidence-based Praise}`
- Meaning: the student experiments across both movement and arm behavior but still ends in a nearly complete solution

7.1 `07_partial_correctness_reassure_a.ndjson`
- StudentID: `fixture_07_1`
- SessionID: `20000000-0000-0000-0007-000000000001`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `HIGH_PERSISTER`
- Intended feedback class(es): `{Partial Correctness, Reassure}`
- Meaning: the student keeps rapidly changing path values for a long session, but the robot still finishes very little

7.2 `07_partial_correctness_reassure_b.ndjson`
- StudentID: `fixture_07_2`
- SessionID: `20000000-0000-0000-0007-000000000002`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `HIGH_PERSISTER`
- Intended feedback class(es): `{Partial Correctness, Reassure}`
- Meaning: the student persistently reworks turning logic and repeatedly tests, yet progress stays low

7.3 `07_partial_correctness_reassure_c.ndjson`
- StudentID: `fixture_07_3`
- SessionID: `20000000-0000-0000-0007-000000000003`
- Intended analyzer cognition: `TRIAL_AND_ERROR`
- Intended analyzer persistence: `HIGH_PERSISTER`
- Intended feedback class(es): `{Partial Correctness, Reassure}`
- Meaning: the student keeps switching between arm and movement fixes over a long session without reaching a stable solution

8.1 `08_diagnose_a.ndjson`
- StudentID: `fixture_08_1`
- SessionID: `20000000-0000-0000-0008-000000000001`
- Intended analyzer cognition: `CODE_ABANDONMENT`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Diagnose}`
- Meaning: the student regresses after deleting a scoring-action block from an otherwise strong solution

8.2 `08_diagnose_b.ndjson`
- StudentID: `fixture_08_2`
- SessionID: `20000000-0000-0000-0008-000000000002`
- Intended analyzer cognition: `CODE_ABANDONMENT`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Diagnose}`
- Meaning: the student regresses after deleting part of the navigation sequence that used to position the robot correctly

8.3 `08_diagnose_c.ndjson`
- StudentID: `fixture_08_3`
- SessionID: `20000000-0000-0000-0008-000000000003`
- Intended analyzer cognition: `CODE_ABANDONMENT`
- Intended analyzer persistence: `EXPECTED_COMPLETION`
- Intended feedback class(es): `{Diagnose}`
- Meaning: the student breaks a previously good mixed strategy and loses progress across more than one subsystem

9.1 `09_reassure_elaborate_a.ndjson`
- StudentID: `fixture_09_1`
- SessionID: `20000000-0000-0000-0009-000000000001`
- Intended analyzer cognition: `CODE_ABANDONMENT`
- Intended analyzer persistence: `HIGH_PERSISTER`
- Intended feedback class(es): `{Reassure, Elaborate}`
- Meaning: after losing a strong solution, the student continues revising for a long session instead of stopping

9.2 `09_reassure_elaborate_b.ndjson`
- StudentID: `fixture_09_2`
- SessionID: `20000000-0000-0000-0009-000000000002`
- Intended analyzer cognition: `CODE_ABANDONMENT`
- Intended analyzer persistence: `HIGH_PERSISTER`
- Intended feedback class(es): `{Reassure, Elaborate}`
- Meaning: the student specifically undoes a working navigation sequence, then keeps iterating hard to recover it

9.3 `09_reassure_elaborate_c.ndjson`
- StudentID: `fixture_09_3`
- SessionID: `20000000-0000-0000-0009-000000000003`
- Intended analyzer cognition: `CODE_ABANDONMENT`
- Intended analyzer persistence: `HIGH_PERSISTER`
- Intended feedback class(es): `{Reassure, Elaborate}`
- Meaning: the student keeps trying both path and action adjustments after the earlier high-progress state collapses
