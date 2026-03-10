from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement

@inlineCallbacks
def nod_head(session):
    """
    Allow for head movement of the robot. A slight up and down movement of the head to show acknowledgement
    """
    yield perform_movement(session,
        frames=[{"time": 600, "data": {"body.head.pitch": 0.174}}, 
                {"time": 1200, "data": {"body.head.pitch": -0.174}},
                {"time": 1800, "data": {"body.head.pitch": 0.174}},
                {"time": 2400, "data": {"body.head.pitch": -0.174}},
                {"time": 3000, "data": {"body.head.pitch": 0.0}}],
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
        {"time": 1300, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": -0.5}},
        {"time": 2100, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": -1.0}},
        {"time": 2900, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": 0.0}},
        {"time": 3700, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": -1.0}},
        {"time": 4500, "data": {"body.arms.right.upper.pitch": -2.5, "body.arms.right.lower.roll": 0.0}},
        {"time": 5800, "data": {"body.arms.right.upper.pitch": -0.5, "body.arms.right.lower.roll": -0.7}},
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
    
@inlineCallbacks
def pause_movement(session):
    """
    Movement to fill pauses
    """
    yield perform_movement(session,
        frames=[{"time": 2000, "data": {"body.head.roll": 0.174, "body.arms.right.upper.pitch": -1.5}},
                {"time": 4000, "data": {"body.head.roll": 0, "body.arms.right.upper.pitch": -0.5}},
                {"time": 4500, "data": {"body.head.roll": 0, "body.arms.right.upper.pitch": -0.5}},
                ],
             force=True)

@inlineCallbacks
def move(session):
    yield perform_movement(session,
        frames=[{"time": 1000, "data": {"body.torso.yaw ": -0.874 }},
            {"time": 2200, "data": {"body.head.pitch": 0, "body.head.yaw": 0}}
                ],
        force=True)
    
@inlineCallbacks
def one_hand_raise(session):
    yield perform_movement(session,
        frames=[{"time": 2200, "data": {"body.arms.right.upper.pitch": -0.9}},
                {"time": 3500, "data": {"body.arms.right.upper.pitch": -0.5}},
                {"time": 4500, "data": {"body.arms.right.upper.pitch": -0.9}},
                {"time": 5500, "data": {"body.arms.right.upper.pitch": -0.5}},
                {"time": 6800, "data": {"body.arms.right.upper.pitch": -0.9}},
                {"time": 8000, "data": {"body.arms.right.upper.pitch": -0.5}},
                {"time": 9000, "data": {"body.arms.right.upper.pitch": -0.5}},
                ], 
                
        force=True)

@inlineCallbacks
def thinking(session):
    """
    Move the robot into a thinking position. 
    Head looks up and hand moves to the chin.
    """
    yield perform_movement(session,
        frames=[{"time": 2200, "data": {"body.head.pitch": -0.174, "body.head.roll": 0.174, "body.arms.left.upper.pitch": -1.5, "body.arms.left.lower.roll": -1.6}},
                {"time": 3800, "data": {"body.head.pitch": -0.174, "body.head.roll": 0, "body.arms.left.upper.pitch": -1.5, "body.arms.left.lower.roll": -1.6}},
                {"time": 5000, "data": {"body.head.pitch": 0.0, "body.head.roll": 0, "body.arms.left.upper.pitch": -0.5, "body.arms.left.lower.roll": -0.7}},
                ],
        force=True)
    
    yield sleep(3)

@inlineCallbacks
def breathing(session):
    """
    Imitation of breathing for a robot.
    """
    yield perform_movement(session,
        frames=[{"time": 2000, "data": {"body.head.roll": -0.05, "body.arms.right.upper.pitch": -0.7, "body.arms.left.upper.pitch": -0.7, "body.torso.yaw": -0.1}},
                {"time": 4000, "data": {"body.head.roll": 0.05, "body.arms.right.upper.pitch": -0.3, "body.arms.left.upper.pitch": -0.3, "body.torso.yaw": 0.1}},
                {"time": 6000, "data": {"body.head.roll": -0.05, "body.arms.right.upper.pitch": -0.7, "body.arms.left.upper.pitch": -0.7, "body.torso.yaw": -0.1}},
                {"time": 8000, "data": {"body.head.roll": 0.05, "body.arms.right.upper.pitch": -0.3, "body.arms.left.upper.pitch": -0.3, "body.torso.yaw": 0.1}},
                {"time": 10000, "data": {"body.head.roll": 0, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5, "body.torso.yaw": 0}},
        ],                   
            force=True)
    
    yield sleep (4)

def turn_head(session):
    """
    """
    yield perform_movement(session,
        frames=[{"time": 3000, "data": {"body.head.pitch": -0.174, "body.head.roll": 0.174}}
        ],
            force=True)
    
def turn_head_back(session):
    yield perform_movement(session,
        frames=[{"time": 3000, "data": {"body.head.pitch": 0, "body.head.roll": 0, "body.head.yaw": 0}}
        ],
            force=True)