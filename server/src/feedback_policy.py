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

    # Evaluate / Stimulate
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
    # Cognition categories (alpha)
    long_term_stalled_progress: bool = False
    development_increases_progress: bool = False
    development_static_progress: bool = False
    development_decreases_progress: bool = False

    # Cognition categories
    trial_and_error: bool = False
    code_abandonment: bool = False
    step_by_step_elimination: bool = False
    snap_n_test: bool = False

    # Persistence categories
    expected_completion: bool = False
    high_persister: bool = False
    early_quitter: bool = False

def determine_feedback_class(x: FeedbackClassInput) -> list[FeedbackClass]:
    feedback_classes = []

    # Long-term stalled progress -> Help out -> c.i
    if x.long_term_stalled_progress:
        feedback_classes.append(FeedbackClass.ERROR_FLAGGING)

    # Development increases progress -> Reflection/Rehearsal -> c.viii
    if x.development_increases_progress:
        feedback_classes.append(FeedbackClass.ELABORATE)

    # Development for static progress -> Motivate to keep persisting -> b.ii
    if x.development_static_progress:
        feedback_classes.append(FeedbackClass.REASSURE)

    # Development decreases progress -> Corrective explanation -> c.ii
    if x.development_decreases_progress:
        feedback_classes.append(FeedbackClass.HOW_TO)

    # Trial & Error -> a.ii
    if x.trial_and_error:
        feedback_classes.append(FeedbackClass.PARTIAL_CORRECTNESS)
        
        # -> b.i
        if x.expected_completion:
            feedback_classes.append(FeedbackClass.EVIDENCE_BASED_PRAISE)

        # -> b.ii
        if x.high_persister:
            feedback_classes.append(FeedbackClass.REASSURE)

        # -> c.ii
        if x.early_quitter:
            feedback_classes.append(FeedbackClass.HOW_TO)

    # Code abandonment
    if x.code_abandonment:

        # -> c.v
        if x.expected_completion or x.early_quitter:
            feedback_classes.append(FeedbackClass.DIAGNOSE)

        # TO DO: always reassure, first two times elaborate, after fill in the blank
        # -> b.ii, c.vii, c.viii
        if x.high_persister:
            feedback_classes.append(FeedbackClass.REASSURE, FeedbackClass.FILL_IN_THE_BLANK, FeedbackClass.ELABORATE)

    # Step-by-step elimination -> c.iv
    if x.step_by_step_elimination:
        feedback_classes.append(FeedbackClass.NUDGE)

    # Snap'n test -> c.ii
    if x.snap_n_test:
        feedback_classes.append(FeedbackClass.HOW_TO)

    return feedback_classes


if __name__ == "__main__":
    x = FeedbackClassInput(
        # Categories determined by Current State Analyzer
        code_abandonment = True,
        early_quitter = True
    )

    feedback_classes = determine_feedback_class(x)
    print("Feedback class:", [fc.value for fc in feedback_classes])