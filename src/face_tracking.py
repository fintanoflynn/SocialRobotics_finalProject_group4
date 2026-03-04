from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement
from alpha_mini_rug.speech_to_text import SpeechToText

    
def on_face(frame):
    """
    Callback - called every time the number of faces the robot sees changes.
    """
    print(frame)

@inlineCallbacks
def find_face(session, active=True):
    """
    Keep searching until a face is found. 
    """
    yield session.call("rie.vision.face.find", active=active)

@inlineCallbacks
def read_faces(session):
    """
    Read faces once (wait until at least 1 face is seen).
    """
    frames = yield session.call("rie.vision.face.read")
    print(frames[0])
    return frames

@inlineCallbacks
def start_face_stream(session):
    """
    Subscribe to face stream and start streaming face data.
    """
    yield session.subscribe(on_face, "rie.vision.face.stream")
    yield session.call("rie.vision.face.stream")

@inlineCallbacks
def track_face(session):
    yield find_face(session, active=True)

    yield session.call('rie.vision.face.track', track_time = 0, lost_time = 400)
    

