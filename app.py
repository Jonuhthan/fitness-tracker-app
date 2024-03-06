from flask import Flask, render_template, Response
from imutils.video import VideoStream
import cv2
import time
import pyzbar

app = Flask(__name__)

def generate():
    # Start the video stream
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    while True:
        # Read each frame
        frame = vs.read()
        _, buffer = cv2.imencode('.jpg', frame)
        # Break the frame down into bytes
        frame = buffer.tobytes()

        # Display the frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

        found = []
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            found.append(barcodeData)
            
        if len(found) > 0:
            break

# Home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
