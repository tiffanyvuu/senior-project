"""
Context Builder
"""

from dataclasses import dataclass, field
from typing import List

from src.feedback_policy import FeedbackClass

@dataclass
class FeedbackSpec:
    description: str
    examples: List[str]
    extra_notes: List[str] = field(default_factory=list)

FEEDBACK_SPECS = {
    "Positive Feedback": FeedbackSpec(
        description="Confirms that the action is fully correct. Clearly identifies what was done correctly and why it works. Focus on the task.",
        examples=[
            "You specified an appropriate distance for the robot to move forward, so it will not fall over the cliff.",
            "You used the [x] block, which allowed the robot to pick up the trash."
        ],
        extra_notes=[
            "Keep the message concise and specific without excessive praise. Emphasize what makes the text correct and the student's apparent reasoning, rather than their abilities."
        ]
    ),
    "Partial Correctness": FeedbackSpec(
        description="Acknowledges what is correct, but also acknowledges what needs adjustment.",
        examples=[
            "You took the correct steps to avoid the debris, but you need to turn right earlier to avoid getting stuck. Make the turn right block appear earlier."
        ],
        extra_notes=[
            "Start with what works, then address what needs revision. Keep feedback manageable and focused on one or two issues, or keep the feedback more high level."
        ]
    ),
    "Corrective Guidance": FeedbackSpec(
        description="Indicates that the action is incorrect and provides clear guidance on how to fix it.",
        examples=[
            "The move forward command runs for too long, which is why your robot falls off the cliff. Replace the distance with something shorter.",
            "Your if block is always going to be true, so your robot will never turn left."
        ],
        extra_notes=[]
    ),
    "Evidence-Based Praise": FeedbackSpec(
        description="Highlights a specific successful action and explains why it was effective. The goal is to encourage effort based on evidence.",
        examples=[
            "Your use of the conditional if statement allows your agent to move in the correct way without requiring a lot of code.",
            "You cleaned up the trash with very few lines of code."
        ],
        extra_notes=[
            "Ensure that praise is tied to a specific accomplishment to avoid directing attention to the self.",
            "As long as the student is making progress, validate their work, which is not the same as praise.",
            "Focus on strategies and decisions, not the person."
        ]
    ),
    "Reassure": FeedbackSpec(
        description="Encourages persistence by reducing student frustration. Validates prior effort and lets them know they are on the right track.",
        examples=[
            "Loops can be tricky. It is very common to have loops run forever until you find the right solution.",
            "You are definitely on the right track and taking the necessary steps. A lot of students struggle with this problem."
        ],
        extra_notes=[]
    ),
    "Error Flagging": FeedbackSpec(
        description="Identifies a specific error clearly and objectively without immediately providing the full solution.",
        examples=[
            "The while statement is always true and will run forever.",
            "You did not connect the two blocks.",
            "The blocks are in the wrong order."
        ],
        extra_notes=[
            "Name the exact issue. Avoid framing it around the person."
        ]
    ),
    "How To": FeedbackSpec(
        description="Provides step-by-step instructions to do a task or solve the problem.",
        examples=[
            "To solve the problem of [problem], take steps a, b, c, and n."
        ],
        extra_notes=[
            "Break the explanation into small steps. Do not overwhelm the student with technical terms."
        ]
    ),
    "Inform": FeedbackSpec(
        description="Provides relevant knowledge about VEX VR components or behavior.",
        examples=[
            "Changing the speed affects how fast you go and how fast you turn."
        ],
        extra_notes=[]
    ),
    "Hint": FeedbackSpec(
        description="Encourages the learner to examine a specific part of their code without giving an explicit solution.",
        examples=[
            "Check where the stop driving block is placed.",
            "Look at the order of each of your commands."
        ],
        extra_notes=[
            "Keep the solution subtle."
        ]
    ),
    "Encourage Testing (Diagnose)": FeedbackSpec(
        description="Guides the learner to test the behavior of the robot to discover the issue independently.",
        examples=[
            "Does the condition in the while block ever become false?",
            "If you reduce the speed, does turning become more accurate?"
        ],
        extra_notes=[
            "Encourage experimentation in the VR environment and develop debugging skills."
        ]
    ),
    "Question": FeedbackSpec(
        description="Provides a focused question to stimulate reasoning about the problem.",
        examples=[
            "How many degrees should the robot turn to face the next obstacle?",
            "At what point does the condition in the block become false?"
        ],
        extra_notes=[
            "Questions should be purposeful."
        ]
    ),
    "Fill-in-the-Blank": FeedbackSpec(
        description="Makes the student recall a concept they are not thinking of or have forgotten.",
        examples=[
            "The _________ block stops all movement.",
            "To implement a condition, use the ___________ block."
        ],
        extra_notes=[
            "Reinforce VEX and programming jargon in the student's memory."
        ]
    ),
    "Elaborate": FeedbackSpec(
        description="Provides a deeper explanation of why something happens.",
        examples=[
            "The robot misses the item because the drive distance is longer than it should be before turning.",
            "The robot continues turning because the turn block or loop is never false."
        ],
        extra_notes=[
            "Do this in small segments."
        ]
    ),
    "Remind": FeedbackSpec(
        description="Restates the robotic goal.",
        examples=[
            "The goal is for the robot to pick up all objects.",
            "Right now, the robot keeps driving because the condition to stop is never met."
        ],
        extra_notes=[
            "This is useful when the learner is possibly misunderstanding the task or outcome."
        ]
    ),
    "Next Step": FeedbackSpec(
        description="Gives a single immediate robotics action to try next.",
        examples=[
            "You could try changing the turn value to 90 degrees and try again.",
            "What if you lower the speed to 75% and test the path?"
        ],
        extra_notes=[
            "Use this as a last resort."
        ]
    )
}

FEEDBACK_CLASS_TO_SPEC_KEY = {
    FeedbackClass.POSITIVE_FEEDBACK: "Positive Feedback",
    FeedbackClass.PARTIAL_CORRECTNESS: "Partial Correctness",
    FeedbackClass.CORRECTIVE_GUIDANCE: "Corrective Guidance",
    FeedbackClass.EVIDENCE_BASED_PRAISE: "Evidence-Based Praise",
    FeedbackClass.REASSURE: "Reassure",
    FeedbackClass.ERROR_FLAGGING: "Error Flagging",
    FeedbackClass.HOW_TO: "How To",
    FeedbackClass.INFORM: "Inform",
    FeedbackClass.NUDGE: "Hint",
    FeedbackClass.DIAGNOSE: "Encourage Testing (Diagnose)",
    FeedbackClass.QUESTION: "Question",
    FeedbackClass.ELABORATE: "Elaborate",
    FeedbackClass.REPEAT: "Remind",
    FeedbackClass.NEXT_STEP: "Next Step",
}

PROMPT_TEMPLATE = """You are an educational feedback assistant for VEXcode VR, a block-based programming tool.

Task:
{task}

Available blocks:
{available_blocks}

Student message:
{student_message}

Raw logs for this student and session:
{raw_logs}

Recent chat in this session:
{recent_chat}

Feedback types to use (combine them in one message):
{feedback_types}

Feedback type descriptions:
{descriptions}

Examples of each feedback type:
{examples}

Extra notes (if any):
{extra_notes}

LLM Instructions (VFF - Enhance learning)

Dos:
- Provide elaborated feedback that describes the what, how, and/or why.
- Present elaborated feedback in manageable units (stepwise, not overwhelming).
- Be specific and clear.
- Keep feedback as simple as possible but no simpler (only enough information to help, and not more).
- Give unbiased, objective feedback.

Don'ts:
- Avoid overall assessment or grading.
- Do not discourage the learner or threaten self-esteem; keep focus on the task.
- Use praise sparingly; avoid directing attention to the self.
- Do not interrupt the learner if they are actively engaged.

Management:
- In extreme cases of long-term struggling or lack of progress, ask the student to defer to a teacher.
- If the student's input is unclear or vague, ask them to restate their question clearly.

Write one short, natural-sounding feedback message for the student that incorporates ALL listed feedback types.
Requirements:
- Use all feedback types in a cohesive way (do not output separate messages).
- Be concise and specific.
- Do not invent details beyond the task and student message.
- When referring to a specific block, wrap only the block name in backticks.
- When mentioning a block, preserve the exact capitalization and wording from the Available blocks list.
"""

def build_feedback_prompt(
    task: str,
    student_message: str,
    available_blocks: str,
    raw_logs: str,
    recent_chat: str,
    feedback_types: list[str],
    feedback_specs: dict,
) -> str:
    feedback_types_text = "\n".join(f"- {t}" for t in feedback_types)

    descriptions_text = "\n\n".join(
        f"{t}:\n{feedback_specs[t].description}"
        for t in feedback_types
    )

    examples_text = "\n\n".join(
        f"{t}:\n" + "\n".join(f"- {e}" for e in feedback_specs[t].examples)
        for t in feedback_types
    )

    extra_notes_text = "\n\n".join(
        f"{t}:\n" + ("\n".join(f"- {n}" for n in feedback_specs[t].extra_notes) if feedback_specs[t].extra_notes else "None")
        for t in feedback_types
    )

    return PROMPT_TEMPLATE.format(
        task=task,
        student_message=student_message,
        available_blocks=available_blocks,
        raw_logs=raw_logs,
        recent_chat=recent_chat,
        feedback_types=feedback_types_text,
        descriptions=descriptions_text,
        examples=examples_text,
        extra_notes=extra_notes_text,
    )


def build_feedback_prompt_from_classes(
    task: str,
    student_message: str,
    available_blocks: list[str] | None,
    raw_logs: str,
    recent_messages: list[dict[str, str]],
    feedback_classes: set[FeedbackClass],
) -> str:
    feedback_types = []
    for feedback_class in feedback_classes:
        feedback_type = FEEDBACK_CLASS_TO_SPEC_KEY.get(feedback_class)
        if feedback_type and feedback_type not in feedback_types:
            feedback_types.append(feedback_type)

    recent_chat = "\n".join(
        f"{message['role'].capitalize()}: {message['content']}"
        for message in recent_messages
    )
    if not recent_chat:
        recent_chat = "None"

    available_blocks_text = "\n".join(f"- {block}" for block in available_blocks or [])
    if not available_blocks_text:
        available_blocks_text = "None provided"

    return build_feedback_prompt(
        task=task,
        student_message=student_message,
        available_blocks=available_blocks_text,
        raw_logs=raw_logs,
        recent_chat=recent_chat,
        feedback_types=feedback_types,
        feedback_specs=FEEDBACK_SPECS,
    )
