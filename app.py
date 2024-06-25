from flask import Flask, render_template, Response, request, redirect
from pyzbar import pyzbar
import cv2
import threading
import requests
import time
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
vs = None
found = []
lock = threading.Lock()
images_dir = r'static\images'
abs_path = os.path.abspath(images_dir)

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


            # Stops generating frames when barcode is found, writes lastframe.jpg to images folder
            if found:
                # cv2.imwrite(os.path.join(abs_path, "lastFrame.jpg"), frame)
                if not cv2.imwrite(os.path.join(abs_path, "last_frame.jpg"), frame):
                    raise Exception("Could not write image.")
                break
            
            _, buffer = cv2.imencode('.jpg', frame)
            # Break the frame down into bytes
            frame = buffer.tobytes()

            # Display the frame
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    # Close video stream
    vs.release()
    vs = None
    cv2.destroyAllWindows()


# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# Calls generate() to display jpg frames on HTML page
@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Initiates feed
@app.route('/start_feed', methods=['POST'])
def start_feed_route():
    global vs
    if vs is None:  # Prevents Video from breaking after repeated presses
        vs = cv2.VideoCapture(cv2.CAP_DSHOW)
    return "Starting video feed"


@app.route('/manual', methods=['POST'])
def man_entry():
    global vs
    barcode = request.form['barcodeField']

    # Update found with manually entered barcode
    found.append(barcode)

    # Prevents result.html from displaying last scanned image
    if os.path.exists(f"{abs_path}/last_frame.jpg"):
        os.remove(f"{abs_path}/last_frame.jpg")
    if not vs is None:
        vs.release()

    # Redirect user to result of barcode scan
    return redirect('/result')


@app.route('/result', methods=['GET', 'POST'])
def result():
    global found
    while True:
        if found:
            break
        time.sleep(2.0)     # Check for barcode every two seconds

    if found:
        barcode = found[0]
        found = []  # Clear for repeated scans on one visit
        product_info = fetch_product_info(barcode)
        return render_template('result.html', product_info=product_info, barcode=barcode, status=status)
    else:
        return render_template('result.html', status=status)


def fetch_product_info(barcode):
    # OpenFoodFacts API
    endpoint = 'https://world.openfoodfacts.org/api/v0/product/'
    url = f'{endpoint}{barcode}.json'   
    response = requests.get(url)
    # JSON representation of data
    data = response.json()
    
    global status
    status = data['status']

    # Different macronutrients and other relevant information to be displayed
    if status == 1:
        product = data['product']
        nutrients = product.get('nutriments', {})
        product_info = {
           'Name': product.get('product_name', 'N/A'),
           'Ingredients': product.get('ingredients_text', 'N/A'),
           'Calories': (
                nutrients.get('energy-kcal_serving', 'N/A'),
                nutrients.get('energy-kcal_unit', 'N/A')
            ),
            'Total Fat': (
                nutrients.get('fat_serving', 'N/A'),
                nutrients.get('fat_unit', 'N/A')
            ),
            'Saturated Fat': (
                nutrients.get('saturated-fat_serving', 'N/A'),
                nutrients.get('saturated-fat_unit', 'N/A')
            ),
            'Trans-fat': (
                nutrients.get('trans-fat_serving', 'N/A'),
                nutrients.get('trans-fat_unit', 'N/A')
            ),
            'Cholesterol': (
                nutrients.get('cholesterol_serving', 'N/A'),
                nutrients.get('cholesterol_unit', 'N/A')
            ),
            'Sodium': (
                nutrients.get('sodium_serving', 'N/A'),
                nutrients.get('sodium_unit', 'N/A')
            ),
            'Total Carbohydrate': (
                nutrients.get('carbohydrates_serving', 'N/A'),
                nutrients.get('carbohydrates_unit', 'N/A')
            ),
            'Fiber': (
                nutrients.get('fiber_serving', 'N/A'),
                nutrients.get('fiber_unit', 'N/A')
            ),
            'Sugar': (
                nutrients.get('sugars_serving', 'N/A'),
                nutrients.get('sugars_unit', 'N/A')
            ),
            'Protein': (
                nutrients.get('proteins_serving', 'N/A'),
                nutrients.get('proteins_unit', 'N/A')
            )
        }
        return product_info
    else:
        return "Product not found or does not exist."


if __name__ == '__main__':
    app.run(debug=True)