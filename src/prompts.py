from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def main(session, active=True):
    yield session.call("rom.optional.behavior.play",
                       name="BlocklyStand")
    
    yield session.call("rie.vision.face.find", active=active)
    yield session.call("rie.dialogue.say", text="Hi!")
    yield session.call("rie.vision.face.track")
    yield session.call("rie.dialogue.say",
                       text="I don't see you anymore!")
    
    yield session.call("rom.optional.behavior.play",
                       name="BlocklyCrouch")
    session.leave()  # Close the connection with the robot

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.69a8062eb788cadff345a4e2"
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
