from io import BytesIO

import streamlit as st
from PIL import Image, ImageOps


st.set_page_config(page_title="Polaroid Maker", page_icon="📸", layout="centered")

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, #263142 0%, #10141d 48%, #090b10 100%);
            color: #eef2f8;
        }
        .hero { padding: 0.5rem 0 1.4rem; text-align: center; }
        .hero h1 { margin-bottom: 0.25rem; color: #ffffff; }
        .hero p { color: #aab5c5; margin: 0; }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #171d29, #0d1017);
            border-right: 1px solid #2a3444;
        }
        [data-testid="stSidebar"] * { color: #e7edf7; }
        [data-testid="stSidebar"] [data-baseweb="slider"] div { color: inherit; }
        [data-testid="stSidebar"] input { color: #e7edf7 !important; }
        [data-testid="stFileUploader"] {
            background: rgba(27, 35, 48, 0.72);
            border-radius: 12px;
            padding: 0.35rem;
        }
        [data-testid="stImage"] img {
            border-radius: 8px;
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.38);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(25, 32, 44, 0.8);
            border-color: #344155;
            border-radius: 16px;
        }
        .stDownloadButton button {
            width: 100%;
            border-radius: 10px;
            background: #7c5cff;
            color: white;
            border: 0;
        }
        .stDownloadButton button:hover { background: #9378ff; color: white; }
    </style>
    <div class="hero">
        <h1>📸 Polaroid Maker</h1>
        <p>Make a keepsake frame without changing your image resolution.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.sidebar.header("Frame settings")
st.sidebar.caption("The download always keeps the uploaded image's dimensions.")

bg_color = st.sidebar.color_picker("Frame color", "#FFFFFF")
image_scale = st.sidebar.slider(
    "Photo size",
    min_value=35,
    max_value=100,
    value=78,
    format="%d%%",
    help="Changes the photo size inside a fixed-size canvas. Smaller photos create a wider frame.",
)
border = st.sidebar.slider("Photo border (px)", 0, 10, 0)
border_color = st.sidebar.color_picker("Photo border color", "#D3D3D3")

uploaded_file = st.file_uploader("Drop in a photo", type=["jpg", "jpeg", "png"])


def create_polaroid(image, bg_color, image_scale, border, border_color):
    """Create a Polaroid while preserving the uploaded image's resolution."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    canvas_width, canvas_height = image.size

    # The canvas is deliberately the same size as the upload. The scale controls
    # the photo within it, rather than adding pixels through configurable margins.
    frame_width = max(1, round(canvas_width * image_scale / 100))
    frame_height = max(1, round(canvas_height * image_scale / 100))
    photo_width = max(1, frame_width - (border * 2))
    photo_height = max(1, frame_height - (border * 2))
    # Avoid resampling altogether when the photo is used at its original size.
    # For smaller frame sizes, LANCZOS provides Pillow's highest-quality resize.
    if (photo_width, photo_height) == image.size:
        photo = image.copy()
    else:
        photo = image.resize((photo_width, photo_height), Image.Resampling.LANCZOS)

    if border:
        photo = ImageOps.expand(photo, border=border, fill=border_color)

    canvas = Image.new("RGB", (canvas_width, canvas_height), bg_color)
    x = (canvas_width - photo.width) // 2
    y = (canvas_height - photo.height) // 2
    canvas.paste(photo, (x, y))
    return canvas


if uploaded_file:
    image = Image.open(uploaded_file)
    result = create_polaroid(image, bg_color, image_scale, border, border_color)

    with st.container(border=True):
        st.caption("LIVE PREVIEW · Download: same resolution as upload")
        # This display is intentionally constrained; it does not affect the file output.
        st.image(result, width=360)

    buffer = BytesIO()
    result.save(buffer, format="JPEG", quality=100, subsampling=0, optimize=True)

    st.download_button(
        label="⬇ Download Polaroid JPEG",
        data=buffer.getvalue(),
        file_name="polaroid.jpg",
        mime="image/jpeg",
    )
else:
    st.info("Upload an image to start designing your Polaroid.")
