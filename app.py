from flask import Flask, render_template, Response
from imutils.video import VideoStream
import cv2
from pyzbar import pyzbar
import threading

app = Flask(__name__)
vs = None
output_frame = None
found = []
lock = threading.Lock()

def generate():
    global vs, output_frame

    while True:
        with lock:
            if vs is None:
                break
            
            # Read each frame and make sure it works
            (success, frame) = vs.read()

            # Check for barcodes
            # barcodes = pyzbar.decode(frame)
            # for barcode in barcodes:
            #     barcodeData = barcode.data.decode("utf-8")
            #     # Append first found barcode to global found
            #     found.append(barcodeData)
            if not success:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            # Break the frame down into bytes
            frame = buffer.tobytes()

            # Display the frame
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # Stops generating frames when barcode is found
            if len(found) > 0:
                break

    vs.release()
    cv2.destroyAllWindows()

# Home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_feed():
    global vs
    vs = cv2.VideoCapture(cv2.CAP_DSHOW)

def stop_feed():
    global vs
    if vs is not None:
        vs.release()

@app.route('/start_feed', methods=['POST'])
def start_feed_route():
    start_feed()
    return "Starting video feed"

@app.route('/stop_feed', methods=['POST'])
def stop_feed_route():
    stop_feed()
    return "Stopping video feed"

if __name__ == '__main__':
    app.run(debug=True)
