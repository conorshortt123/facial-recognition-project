import threading
from prototype import app
from prototype.routes import recognize_face

# check to see if this is the main thread of execution
if __name__ == '__main__':
    # start a thread that will perform face recognition
    t = threading.Thread(target=recognize_face)
    t.daemon = True
    t.start()

    # start the flask app
    app.run(debug=True, threaded=True, use_reloader=False)
