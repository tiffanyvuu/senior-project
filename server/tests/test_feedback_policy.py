from server.src.feedback_policy import (
    FeedbackClass,
    FeedbackClassInput,
    determine_feedback_class,
)


def test_returns_empty_set_when_no_flags():
    result = determine_feedback_class(FeedbackClassInput())
    assert result == set()


def test_long_term_stalled_progress():
    result = determine_feedback_class(
        FeedbackClassInput(long_term_stalled_progress=True)
    )
    assert result == {FeedbackClass.ERROR_FLAGGING}


def test_development_increases_progress():
    result = determine_feedback_class(
        FeedbackClassInput(development_increases_progress=True)
    )
    assert result == {FeedbackClass.ELABORATE}


def test_development_static_progress():
    result = determine_feedback_class(
        FeedbackClassInput(development_static_progress=True)
    )
    assert result == {FeedbackClass.REASSURE}


def test_development_decreases_progress():
    result = determine_feedback_class(
        FeedbackClassInput(development_decreases_progress=True)
    )
    assert result == {FeedbackClass.INFORM}


def test_trial_and_error_baseline():
    result = determine_feedback_class(FeedbackClassInput(trial_and_error=True))
    assert result == {FeedbackClass.PARTIAL_CORRECTNESS}


def test_trial_and_error_with_expected_completion():
    result = determine_feedback_class(
        FeedbackClassInput(trial_and_error=True, expected_completion=True)
    )
    assert result == {
        FeedbackClass.PARTIAL_CORRECTNESS, FeedbackClass.EVIDENCE_BASED_PRAISE}


def test_trial_and_error_with_high_persister():
    result = determine_feedback_class(
        FeedbackClassInput(trial_and_error=True, high_persister=True)
    )
    assert result == {FeedbackClass.PARTIAL_CORRECTNESS, FeedbackClass.REASSURE}


def test_trial_and_error_with_early_quitter():
    result = determine_feedback_class(
        FeedbackClassInput(trial_and_error=True, early_quitter=True)
    )
    assert result == {FeedbackClass.PARTIAL_CORRECTNESS, FeedbackClass.HOW_TO}


def test_code_abandonment_with_expected_completion():
    result = determine_feedback_class(
        FeedbackClassInput(code_abandonment=True, expected_completion=True)
    )
    assert result == {FeedbackClass.DIAGNOSE}


def test_code_abandonment_with_early_quitter():
    result = determine_feedback_class(
        FeedbackClassInput(code_abandonment=True, early_quitter=True)
    )
    assert result == {FeedbackClass.DIAGNOSE}


def test_code_abandonment_with_high_persister():
    result = determine_feedback_class(
        FeedbackClassInput(code_abandonment=True, high_persister=True)
    )
    assert result == {FeedbackClass.REASSURE, FeedbackClass.ELABORATE}


def test_step_by_step_elimination():
    result = determine_feedback_class(
        FeedbackClassInput(step_by_step_elimination=True)
    )
    assert result == {FeedbackClass.NUDGE}


def test_snap_n_test():
    result = determine_feedback_class(FeedbackClassInput(snap_n_test=True))
    assert result == {FeedbackClass.INFORM}


def test_combined_inputs_are_union_without_duplicates():
    result = determine_feedback_class(
        FeedbackClassInput(
            development_decreases_progress=True,
            trial_and_error=True,
            early_quitter=True,
            code_abandonment=True,
            expected_completion=True,
            snap_n_test=True,
        )
    )
    assert result == {
        FeedbackClass.INFORM,
        FeedbackClass.PARTIAL_CORRECTNESS,
        FeedbackClass.HOW_TO,
        FeedbackClass.DIAGNOSE,
        FeedbackClass.EVIDENCE_BASED_PRAISE,
    }
