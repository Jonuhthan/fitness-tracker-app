from imutils.video import VideoStream
from pyzbar import pyzbar

def get_barcode():
    # start video stream
    vs = VideoStream(src=0).start()
    # list of barcodes scanned
    found = []

    while True:
        # check each frame for a barcode
        frame = vs.read()
        barcodes = pyzbar.decode(frame)

        # grab data from each barcode and add to list
        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            found.append(barcodeData)
        
        # video stream ends once barcode is found
        if len(found) > 0:
            break
    
    # returns barcode number
    vs.stop()
    return found