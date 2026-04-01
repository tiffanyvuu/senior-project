TASK_DESCRIPTIONS = {
    "default": "Help the student debug and improve their VEXcode VR program.",
    "MarsMathExpedition": "The student is working in VEXcode VR Mars Math Expedition, a block-based robotics activity where they program the Competition Advanced Hero Bot to score as many points as possible in one minute. Each challenge task is worth 1 point, so success depends on choosing which tasks to complete and in what order. The robot can drive forward and backward, turn, raise and lower its arm, and use an eye sensor to detect objects and object colors. Relevant blocks include Drive for, Turn for, Spin arm motor, Spin arm motor to position, and Wait until with the eye sensor. Common tasks include moving a sample out of a crater, moving the robot or rover out of the crater, placing a sample on the Lab, lifting the Rocket Ship upright, tilting the Solar Panel down, and removing Fuel Cells from the cradles.",
}


def resolve_task_description(playground: str) -> str:
    return TASK_DESCRIPTIONS.get(playground, TASK_DESCRIPTIONS["default"])
