from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)


MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'best.pt')
model = YOLO(MODEL_PATH)

CLASS_LABELS = {
    0: "Pothole",
    1: "Pipeline Leakage",
    2: "Garbage",
    3: "Manhole",
    4: "Fallen Tree",
}


@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Read the image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        # Run inference with lower confidence threshold
        results = model(image, conf=0.15)

        if results and len(results) > 0:
            result = results[0]

            if result.boxes and len(result.boxes) > 0:
                # Get the detection with highest confidence
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy().astype(int)

                best_idx = confidences.argmax()
                class_id = int(class_ids[best_idx])
                confidence = float(confidences[best_idx])

                label = CLASS_LABELS.get(class_id, f"Unknown (class {class_id})")

                return jsonify({
                    'success': True,
                    'class_id': class_id,
                    'label': label,
                    'confidence': round(confidence * 100, 2)
                })
            else:
                return jsonify({
                    'success': True,
                    'class_id': None,
                    'label': 'No issue detected',
                    'confidence': 0
                })
        else:
            return jsonify({
                'success': True,
                'class_id': None,
                'label': 'No issue detected',
                'confidence': 0
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model_loaded': model is not None})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
