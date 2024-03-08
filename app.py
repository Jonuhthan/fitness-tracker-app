from flask import Flask, render_template, Response
from imutils.video import VideoStream
import cv2
from pyzbar import pyzbar
import threading
import time

app = Flask(__name__)
vs = None
found = []
lock = threading.Lock()

def generate():
    global vs

    while True:
        with lock:
            if vs is None:
                print('Video Stream returned None.')
                break
                    
            # Read each frame and make sure it works
            success, frame = vs.read()
            
            if not success:
                print('Failed to read frame.')
                break
            
            # Check each successful frame for barcodes
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                
                # Grab number and type
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type

                # Show the barcode info in the video stream
                text = f"{barcodeData} ({barcodeType})"
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Append first found barcode to global found
                found.append(barcodeData)
            
            _, buffer = cv2.imencode('.jpg', frame)
            # Break the frame down into bytes
            frame = buffer.tobytes()

            # Display the frame
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # Stops generating frames when barcode is found
            if len(found) > 0:
                print(f"Barcode scanned: {barcodeData}")
                break
    # Close video stream
    vs.release()
    cv2.destroyAllWindows()


# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Calls generate() to display jpg frames on HTML page
@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_feed():
    global vs
    if vs is None:  # Prevents Video from breaking after repeated presses
        vs = cv2.VideoCapture(cv2.CAP_DSHOW)

@app.route('/start_feed', methods=['POST'])
def start_feed_route():
    start_feed()
    return "Starting video feed"


if __name__ == '__main__':
    app.run(debug=True)