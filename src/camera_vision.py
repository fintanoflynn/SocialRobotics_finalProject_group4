from twisted.internet.defer import inlineCallbacks

def on_face(frame):
    ...

@inlineCallbacks
def find_face(session, active=True):
    """
    Makes the robot move its head to see if it can find a face.

    Args:
        session: The session object to communicate with the robot.
        active (bool): If True, the robot will actively search for a face by moving its head.
                       If False, the robot will only look ahead until it finds a face.
    """
    try:
        result = yield session.call("rie.vision.face.find", active=active)
        print("Face found:", result)
        return result
    except Exception as e:
        print("Error finding face:", e)
        return None

def main(session, detail):
    frames = yield session.call("rie.vision.face.read")
    print(frames)

    yield session.subscribe(on_face, "rie.vision.face.stream")
    yield session.call("rie.vision.face.stream")