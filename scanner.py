from imutils.video import VideoStream
from pyzbar import pyzbar
import time

def get_barcode():
    # Start video stream
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    # List of barcodes scanned
    found = []

    while True:
        # Check each frame for a barcode
        frame = vs.read()
        barcodes = pyzbar.decode(frame)

        # Grab data from each barcode and add to list
        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            found.append(barcodeData)
        
        # Video stream ends once barcode is found
        if len(found) > 0:
            break
    
    # Returns barcode number
    vs.stop()
    return found

get_barcode()