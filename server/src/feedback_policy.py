"""
Feedback Policy
"""

from enum import Enum
from dataclasses import dataclass

class FeedbackClass(Enum):
    # Acknowledge / Notify
    POSITIVE_FEEDBACK = "Positive Feedback"
    PARTIAL_CORRECTNESS = "Partial Correctness"
    CORRECTIVE_GUIDANCE = "Corrective Guidance"

    # Motivate
    EVIDENCE_BASED_PRAISE = "Evidence-based Praise"
    REASSURE = "Reassure"
    NEUTRAL = "Neutral"

    # Evaluate / Stimulate thinking
    ERROR_FLAGGING = "Error Flagging"
    HOW_TO = "How To"
    INFORM = "Inform"
    NUDGE = "Nudge"
    DIAGNOSE = "Diagnose"
    QUESTION = "Question"
    FILL_IN_THE_BLANK = "Fill-in-the-blank"
    ELABORATE = "Elaborate"
    REPEAT = "Repeat"
    NEXT_STEP = "Next Step"

@dataclass
class FeedbackClassInput:
    # Cognition / progress patterns
    long_term_stalled_progress: bool = False
    development_increases_progress: bool = False
    development_static_progress: bool = False
    development_decreases_progress: bool = False

    # Cognition / behavior patterns
    trial_and_error: bool = False
    code_abandonment: bool = False
    step_by_step_elimination: bool = False
    snap_n_test: bool = False

    # Persistence
    expected_completion: bool = False
    high_persister: bool = False
    early_quitter: bool = False

def determine_feedback_class(x: FeedbackClassInput) -> FeedbackClass:
    # Long-term stalled progress -> Help out -> c.i
    if x.long_term_stalled_progress:
        return FeedbackClass.ERROR_FLAGGING

    # Development increases progress -> Reflection/Rehearsal -> c.viii
    if x.development_increases_progress:
        return FeedbackClass.ELABORATE

    # Development for static progress -> Motivate to keep persisting -> b.ii
    if x.development_static_progress:
        return FeedbackClass.REASSURE

    # Development decreases progress -> Corrective explanation -> c.ii
    if x.development_decreases_progress:
        return FeedbackClass.HOW_TO

    # Trial & Error -> a.ii
    if x.trial_and_error:
        return FeedbackClass.PARTIAL_CORRECTNESS

    # Code abandonment -> c.v
    if x.code_abandonment:
        return FeedbackClass.DIAGNOSE

    # Step-by-step elimination -> c.iv
    if x.step_by_step_elimination:
        return FeedbackClass.NUDGE

    # Snap'n test -> c.ii
    if x.snap_n_test:
        return FeedbackClass.HOW_TO

    # Fallback 
    return FeedbackClass.NEUTRAL


if __name__ == "__main__":
    x = FeedbackClassInput(
        long_term_stalled_progress = True
    )

    feedback_class = determine_feedback_class(x)
    print("Feedback class:", feedback_class.value)