from flask import Flask, render_template, Response
from imutils.video import VideoStream
from pyzbar import pyzbar
import cv2
import threading
import requests

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

@app.route('/result', methods=['POST'])
def result():
    global found
    # Constantly check for barcode
    while not found:
        continue
    if found:
        barcode = found[0]  #'0078742136035'   # Chocolate bar barcode example
        product_info = fetch_product_info(barcode)
        return render_template('result.html', product_info=product_info, barcode=barcode, status=status)
    else:
        return "No barcode recognized"

def fetch_product_info(barcode):
    # OpenFoodFacts API
    endpoint = 'https://world.openfoodfacts.org/api/v0/product/'
    url = f'{endpoint}{barcode}.json'   
    response = requests.get(url)
    # JSON representation of data
    data = response.json()
    
    global status
    status = data['status']

    if status == 1:
        product = data['product']
        nutrients = product.get('nutriments', {})
        # Key-value pairs of relevant nutritional info (will be edited in the future)
        product_info = {
           'Name': product.get('product_name', 'N/A'),
           'allergens': product.get('allergens_from_ingredients', 'N/A'),
           'serving_size': product.get('serving_size', 'N/A'),
           'ingredients': product.get('ingredients_text', 'N/A'),
      
           'fat': nutrients.get('fat', 'N/A'),
           'fat_unit': nutrients.get('fat_unit', ''),
           'cholesterol': nutrients.get('cholesterol', 'N/A'),
           'cholesterol_unit': nutrients.get('cholesterol_unit', ''),
           'sodium': nutrients.get('sodium', 'N/A'),
           'sodium_unit': nutrients.get('sodium_unit', ''),
           'carbohydrates': nutrients.get('carbohydrates', 'N/A'),
           'carbohydrates_unit': nutrients.get('carbohydrates_unit', ''),
           'sugars': nutrients.get('sugars', 'N/A'),
           'sugars_unit': nutrients.get('sugars_unit', ''),
           'proteins': nutrients.get('proteins', 'N/A'),
           'proteins_unit': nutrients.get('proteins_unit', '')
       }
        return product_info
    else:
        return "Product not found or does not exist."


if __name__ == '__main__':
    app.run(debug=True)