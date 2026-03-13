from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def find_face(session, active=True):
    try:
        result = yield session.call("rie.vision.face.find", active=active)
        print("Face found:", result)
        return result
    except Exception as e:
        print("Error finding face:", e)
        return None