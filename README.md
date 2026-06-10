# Civic Issue Detector

A Streamlit app that uses a YOLO model to detect urban civic issues from images.

## What it does

- Detects the following civic issues in uploaded images:
  - Pothole
  - Pipeline Leakage
  - Garbagee
- Shows a detection result with confidence and a short issue description.

## Files

- `streamlit_app.py` - main Streamlit application.
- `best.pt` - trained YOLO model weights used for inference.
- `requirements.txt` - Python dependencies required to run the app.
- `model.py` - dataset preparation script used for merging and labeling training data.
- `packages.txt` - additional package references (optional).

## Requirements

- Python 3.10+ recommended
- `pip` package manager

## Installation

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/Scripts/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. If OpenCV issues occur, the app includes a fix that installs `opencv-python-headless`.

## Run the app

From the project directory, run:

```bash
streamlit run streamlit_app.py
```

Then open the local URL shown in the terminal.

## Usage

1. Upload an image in JPG, JPEG, PNG, or WEBP format.
2. The app runs inference against `best.pt`.
3. The detected issue and confidence score are displayed.

## Notes

- Make sure `best.pt` is present in the project folder before running the app.
- The app uses `ultralytics.YOLO` for inference.
- `model.py` is not required to run the app, but it contains dataset preparation steps for training.

## License

This project does not include a license file. Add one if you want to share or publish it publicly.
