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

def determine_feedback_class(x: FeedbackClassInput) -> list[FeedbackClass]:
    feedback_classes = []

    # Long-term stalled progress -> Help out -> c.i
    if x.long_term_stalled_progress:
        return [FeedbackClass.ERROR_FLAGGING]

    # Development increases progress -> Reflection/Rehearsal -> c.viii
    if x.development_increases_progress:
        return [FeedbackClass.ELABORATE]

    # Development for static progress -> Motivate to keep persisting -> b.ii
    if x.development_static_progress:
        return [FeedbackClass.REASSURE]

    # Development decreases progress -> Corrective explanation -> c.ii
    if x.development_decreases_progress:
        return [FeedbackClass.HOW_TO]

    # Trial & Error -> a.ii, c.ii, b.ii, b.i
    if x.trial_and_error:
        feedback_classes.extend([FeedbackClass.PARTIAL_CORRECTNESS, FeedbackClass.HOW_TO, FeedbackClass.REASSURE, FeedbackClass.EVIDENCE_BASED_PRAISE])

    # Code abandonment -> c.v
    if x.code_abandonment:
        feedback_classes.extend([FeedbackClass.DIAGNOSE, FeedbackClass.REASSURE, FeedbackClass.FILL_IN_THE_BLANK, FeedbackClass.ELABORATE])

    # Step-by-step elimination -> c.iv
    if x.step_by_step_elimination:
        feedback_classes.append(FeedbackClass.NUDGE)

    # Snap'n test -> c.ii
    if x.snap_n_test:
        feedback_classes.append(FeedbackClass.HOW_TO)

    # Expected completion -> b.i, c.v
    if x.expected_completion:
        feedback_classes.extend([FeedbackClass.EVIDENCE_BASED_PRAISE, FeedbackClass.DIAGNOSE])

    # High persister -> b.ii, c.vii, c.viii
    if x.high_persister:
        feedback_classes.extend([FeedbackClass.REASSURE, FeedbackClass.FILL_IN_THE_BLANK, FeedbackClass.ELABORATE])

    # Early quitter -> c.ii, c.v
    if x.early_quitter:
        feedback_classes.extend([FeedbackClass.HOW_TO, FeedbackClass.DIAGNOSE])

    # Fallback 
    return feedback_classes if feedback_classes else [FeedbackClass.NEUTRAL]


if __name__ == "__main__":
    x = FeedbackClassInput(
        code_abandonment=True,
        step_by_step_elimination=True
    )

    feedback_classes = determine_feedback_class(x)
    print("Feedback class:", [fc.value for fc in feedback_classes])