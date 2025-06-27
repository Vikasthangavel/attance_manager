from flask import Flask, render_template, request, jsonify
import cv2
import requests
import numpy as np
from pyzbar.pyzbar import decode

app = Flask(__name__)

# Your Google Apps Script Web App URL
SCRIPT_URL = "https://script.google.com/macros/s/AKfzAAv/exec"

def scan_qr():
    cap = cv2.VideoCapture(0)  # Open webcam
    scanned_qr = None

    while True:
        _, frame = cap.read()  # Capture frame
        for barcode in decode(frame):
            qr_data = barcode.data.decode("utf-8")  # Extract QR data
            scanned_qr = qr_data
            print(f"Scanned QR Code: {qr_data}")

            # Highlight QR code in frame
            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
            cv2.putText(frame, qr_data, (barcode.rect.left, barcode.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or scanned_qr:
            break

    cap.release()
    cv2.destroyAllWindows()
    return scanned_qr

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan_old_qr")
def scan_old_qr():
    old_qr = scan_qr()
    return jsonify({"oldQR": old_qr})

@app.route("/scan_new_qr")
def scan_new_qr():
    new_qr = scan_qr()
    return jsonify({"newQR": new_qr})

@app.route("/update_qr", methods=["POST"])
def update_qr():
    data = request.json
    old_qr = data.get("oldQR")
    new_qr = data.get("newQR")

    if not old_qr or not new_qr:
        return jsonify({"error": "Missing QR codes"}), 400

    params = {"oldQR": old_qr, "newQR": new_qr}
    response = requests.get(SCRIPT_URL, params=params)
    
    return jsonify({"message": response.text})

if __name__ == "__main__":
    app.run(debug=True)
