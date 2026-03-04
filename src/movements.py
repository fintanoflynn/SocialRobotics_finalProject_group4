from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement
from alpha_mini_rug.speech_to_text import SpeechToText




@inlineCallbacks
def nod_head(session):
    """
    Allow for head movement of the robot. A slight up and down movement of the head to show acknowledgement
    """
    yield perform_movement(session,
        frames=[{"time": 400, "data": {"body.head.pitch": 0.174}}, 
                {"time": 800, "data": {"body.head.pitch": -0.174}},
                {"time": 1200, "data": {"body.head.pitch": 0.174}},
                {"time": 1600, "data": {"body.head.pitch": -0.174}},
                {"time": 2200, "data": {"body.head.pitch": 0.0}}],
        force=True)
    yield sleep(2)


@inlineCallbacks
def shake_head(session):
    """
    Shake the head to show that the robot did not understand the speaker. 
    """
    yield perform_movement(session,
        frames=[{"time": 600, "data": {"body.head.yaw": 0.174}}, 
                {"time": 1200, "data": {"body.head.yaw": -0.174}},
                {"time": 1800, "data": {"body.head.yaw": 0.174}},
                {"time": 2400, "data": {"body.head.yaw": -0.174}},
                {"time": 3000, "data": {"body.head.yaw": 0.174}},
                {"time": 4000, "data": {"body.head.yaw": 0.0}}],
        force=True)
    yield sleep(2)

@inlineCallbacks
def wave_right_arm(session):
    print("DEBUG: using NEW wave_right_arm with rom.actuator.motor.write")

    frames = [
        {"time": 1200, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": -0.5}},
        {"time": 1800, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": -1.0}},
        {"time": 2500, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": 0.0}},
        {"time": 3000, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": -1.0}},
        {"time": 3800, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": 0.0}},
        {"time": 4700, "data": {"body.arms.right.upper.pitch": -0.5, "body.arms.right.lower.roll": -0.7}},
    ]

    try:
        result = yield session.call(
            "rom.actuator.motor.write",
            frames=frames,
            force=True,
        )
        print("motor write result:", result)
    except Exception as e:
        print("motor write failed:", repr(e))
        raise

    yield sleep(1)

@inlineCallbacks
def raise_hands(session):
    """
    Raise hands to show that the robot is celebrating. 
    """
    yield perform_movement(session,
        frames=[{"time": 2200, "data": {"body.arms.left.upper.pitch": -0.5, "body.arms.right.upper.pitch": -0.5}},
                {"time": 3500, "data": {"body.arms.left.upper.pitch": -2.7, "body.arms.right.upper.pitch": -2.5}},
                {"time": 4500, "data": {"body.arms.left.upper.pitch": -1.0, "body.arms.right.upper.pitch": -1.0}},
                {"time": 5500, "data": {"body.arms.left.upper.pitch": -2.7, "body.arms.right.upper.pitch": -2.5}},
                {"time": 6800, "data": {"body.arms.left.upper.pitch": -1.0, "body.arms.right.upper.pitch": -1.0}},
                {"time": 8000, "data": {"body.arms.left.upper.pitch": -2.5, "body.arms.right.upper.pitch": -2.5}},
                {"time": 9000, "data": {"body.arms.left.upper.pitch": -0.5, "body.arms.right.upper.pitch": -0.5}},
                ], 
                
        force=True)
