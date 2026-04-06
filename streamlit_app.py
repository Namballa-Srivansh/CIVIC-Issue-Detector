import streamlit as st
import os

@st.cache_resource
def fix_opencv():
    os.system("pip uninstall -y opencv-python opencv-python-headless")
    os.system("pip install opencv-python-headless")
    return True

fix_opencv()

from PIL import Image
from ultralytics import YOLO

# Must be first
st.set_page_config(page_title="Civic Issue Detector", page_icon="🏙️", layout="centered")

@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best.pt')
    if os.path.exists(path):
        return YOLO(path)
    return None

model = load_model()

CLASS_LABELS = {
    0: "Pothole",
    1: "Pipeline Leakage",
    2: "Garbage",
    3: "Manhole",
    4: "Fallen Tree",
}

ISSUE_CONFIG = {
    'Pothole': {'icon': '🕳️', 'cssClass': 'pothole', 'description': 'Road surface damage detected. This can cause vehicle damage and safety hazards.'},
    'Pipeline Leakage': {'icon': '💧', 'cssClass': 'pipeline-leakage', 'description': 'Water/gas pipeline leak detected. Immediate maintenance is recommended.'},
    'Garbage': {'icon': '🗑️', 'cssClass': 'garbage', 'description': 'Waste accumulation detected. Sanitation services should be notified.'},
    'Manhole': {'icon': '🔘', 'cssClass': 'manhole', 'description': 'Open or damaged manhole detected. This poses a serious pedestrian safety risk.'},
    'Fallen Tree': {'icon': '🌳', 'cssClass': 'fallen-tree', 'description': 'A fallen tree has been detected. It may block roads and cause hazards.'},
    'No issue detected': {'icon': '✅', 'cssClass': 'no-issue', 'description': 'No civic issues were detected in this image.'},
}

st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: white;
}
.ambient {
    position: fixed; inset: 0; pointer-events: none; overflow: hidden; z-index: 0;
}
.blob { position: absolute; border-radius: 50%; filter: blur(120px); }
.blob-1 { top: -20%; right: -10%; width: 600px; height: 600px; background: rgba(99,102,241,0.15); }
.blob-2 { bottom: -20%; left: -10%; width: 500px; height: 500px; background: rgba(147,51,234,0.15); }

header { visibility: hidden; }
footer { visibility: hidden; }

.glass-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 20px;
}

.custom-header { text-align: center; margin-bottom: 30px; animation: fade-in-up 0.6s ease-out; }
.badge {
    display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px;
    border-radius: 9999px; background: rgba(99,102,241,0.10);
    border: 1px solid rgba(99,102,241,0.20); color: #a5b4fc; font-size: 0.85rem; margin-bottom: 24px;
}
.custom-title { font-size: 3rem; font-weight: 800; line-height: 1.15; margin-bottom: 16px; }
.custom-title span { background: linear-gradient(to right, #ffffff, #c7d2fe, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.custom-subtitle { color: #94a3b8; font-size: 1.1rem; }

.result-badge { text-align: center; padding: 32px; border-radius: 14px; margin-bottom: 20px; }
.result-badge.pothole { background: rgba(245,158,11,0.10); border: 1px solid rgba(245,158,11,0.30); }
.result-badge.pipeline-leakage { background: rgba(59,130,246,0.10); border: 1px solid rgba(59,130,246,0.30); }
.result-badge.garbage { background: rgba(34,197,94,0.10); border: 1px solid rgba(34,197,94,0.30); }
.result-badge.manhole { background: rgba(239,68,68,0.10); border: 1px solid rgba(239,68,68,0.30); }
.result-badge.fallen-tree { background: rgba(20,184,166,0.10); border: 1px solid rgba(20,184,166,0.30); }
.result-badge.no-issue { background: rgba(100,116,139,0.10); border: 1px solid rgba(100,116,139,0.30); }
.result-emoji { font-size: 3.5rem; margin-bottom: 16px; display: block;}
.result-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 8px;}
.result-title.pothole { color: #fbbf24; }
.result-title.pipeline-leakage { color: #60a5fa; }
.result-title.garbage { color: #34d399; }
.result-title.manhole { color: #f87171; }
.result-title.fallen-tree { color: #2dd4bf; }
.result-title.no-issue { color: #94a3b8; }
.result-desc { color: #94a3b8; font-size: 0.88rem; line-height: 1.6; }

.conf-box { background: rgba(15,23,42,0.5); border: 1px solid rgba(51,65,85,0.5); border-radius: 14px; padding: 16px; }
.conf-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
.conf-label { color: #94a3b8; font-size: 0.85rem;}
.conf-val { font-weight: 700; font-size: 1.15rem; color: white;}
.conf-track { width: 100%; height: 12px; background: rgba(51,65,85,0.5); border-radius: 9999px; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 9999px; }

.info-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px;}
.info-col { flex: 1; min-width: 140px; background: rgba(15, 23, 42, 0.6); padding: 15px; border-radius: 10px; border: 1px solid rgba(99,102,241,0.15); display: flex; align-items:center; gap: 10px;}
.info-col p { margin: 0; font-size: 0.85rem; color: #94a3b8;}
.info-col .ic-title { font-weight: bold; margin-bottom: 2px;}

@keyframes spin-slow { 100% { transform: rotate(360deg); } }
</style>

<div class="ambient">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
</div>
""", unsafe_allow_html=True)


# --- UI Layout ---

st.markdown("""
<div class="custom-header">
    <div class="custom-title"><span>Civic Issue<br>Detector</span></div>
    <div class="custom-subtitle">Upload a photo to instantly detect potholes, pipeline leakages, garbage.</div>
</div>
""", unsafe_allow_html=True)

if not model:
    st.error("Model best.pt not found. Make sure best.pt is in the same directory.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="glass-card"><h4>Upload Image</h4>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload an image", label_visibility="collapsed", type=['jpg', 'jpeg', 'png', 'webp'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, use_container_width=True, caption="Uploaded Image")

with col2:
    st.markdown('<div class="glass-card"><h4>Detection Result</h4>', unsafe_allow_html=True)
    
    if uploaded_file:
        with st.spinner("Analyzing image..."):
            # Run inference
            results = model(image, conf=0.15)
            
            detected = False
            if results and len(results) > 0:
                result = results[0]
                if result.boxes and len(result.boxes) > 0:
                    confidences = result.boxes.conf.cpu().numpy()
                    class_ids = result.boxes.cls.cpu().numpy().astype(int)

                    best_idx = confidences.argmax()
                    class_id = int(class_ids[best_idx])
                    confidence = float(confidences[best_idx])

                    label = CLASS_LABELS.get(class_id, "Unknown")
                    detected = True
            
            if detected:
                display_label = label
                display_conf = confidence * 100
            else:
                display_label = 'No issue detected'
                display_conf = 0.0

            cfg = ISSUE_CONFIG.get(display_label, ISSUE_CONFIG['No issue detected'])
            c_class = cfg['cssClass']
            
            # Helper for gradient colors
            gradients = {
                'pothole': 'linear-gradient(to right, #f59e0b, #ea580c)',
                'pipeline-leakage': 'linear-gradient(to right, #3b82f6, #06b6d4)',
                'garbage': 'linear-gradient(to right, #22c55e, #10b981)',
                'manhole': 'linear-gradient(to right, #ef4444, #dc2626)',
                'fallen-tree': 'linear-gradient(to right, #14b8a6, #0d9488)',
                'no-issue': 'linear-gradient(to right, #64748b, #475569)'
            }
            grad = gradients.get(c_class, gradients['no-issue'])

            st.markdown(f"""
            <div class="result-badge {c_class}">
                <span class="result-emoji">{cfg['icon']}</span>
                <div class="result-title {c_class}">{display_label}</div>
                <div class="result-desc">{cfg['description']}</div>
            </div>
            
            <div class="conf-box">
                <div class="conf-header">
                    <span class="conf-label">Confidence</span>
                    <span class="conf-val" style="color: {grad.split(',')[1].strip()}">{display_conf:.1f}%</span>
                </div>
                <div class="conf-track">
                    <div class="conf-fill" style="width: {display_conf}%; background: {grad}"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="text-align:center; padding: 40px; color: #64748b;">
            <p>No results yet<br>Upload an image to analyze</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer Info Cards
st.markdown("""
<div class="info-row">
    <div class="info-col"><span>🕳️</span><div><div class="ic-title" style="color:#fbbf24">Potholes</div><p>Road damage</p></div></div>
    <div class="info-col"><span>💧</span><div><div class="ic-title" style="color:#60a5fa">Leaks</div><p>Water/gas leakage</p></div></div>
    <div class="info-col"><span>🗑️</span><div><div class="ic-title" style="color:#34d399">Garbage</div><p>Waste accumulation</p></div></div>
</div>
<div style="text-align:center; margin-top: 40px; color: #475569; font-size: 0.85rem;">
    Civic Issue Detector — Powered by YOLO & Streamlit
</div>
""", unsafe_allow_html=True)
