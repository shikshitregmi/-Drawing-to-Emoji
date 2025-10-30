import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image
import io
import base64


class DrawingCanvas:
    def __init__(self, width=400, height=400):
        self.width = width
        self.height = height
        self.drawing_mode = "freedraw"
        self.stroke_width = st.session_state.get('stroke_width', 10)
        self.stroke_color = st.session_state.get('stroke_color', "#000000")
        self.bg_color = st.session_state.get('bg_color', "#FFFFFF")

    def render_canvas(self, key="canvas"):
        """Render the drawing canvas"""
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            background_color=self.bg_color,
            width=self.width,
            height=self.height,
            drawing_mode=self.drawing_mode,
            point_display_radius=0,
            key=key,
        )
        return canvas_result

    def get_image_data(self, canvas_result):
        """Extract image data from canvas result"""
        if canvas_result.image_data is not None:
            return canvas_result.image_data
        return None

    def convert_to_pil_image(self, image_data):
        """Convert canvas image data to PIL Image"""
        if image_data is not None:
            # Convert to PIL Image
            img_data = image_data.astype(np.uint8)
            pil_image = Image.fromarray(img_data)
            return pil_image
        return None

    def preprocess_image(self, pil_image, target_size=(64, 64)):
        """Preprocess image for model input"""
        if pil_image:
            # Convert to grayscale and resize
            processed = pil_image.convert('L').resize(target_size)
            return np.array(processed) / 255.0
        return None

    def clear_canvas(self):
        """Clear the canvas by resetting session state"""
        if 'canvas_key' in st.session_state:
            st.session_state.canvas_key += 1
        else:
            st.session_state.canvas_key = 1


def render_drawing_controls():
    """Render drawing controls sidebar"""
    st.sidebar.header("🎨 Drawing Controls")

    # Brush settings
    stroke_width = st.sidebar.slider("Brush Size", 1, 30, 10, key="stroke_width")
    stroke_color = st.sidebar.color_picker("Brush Color", "#000000", key="stroke_color")
    bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF", key="bg_color")

    # Drawing tools
    drawing_mode = st.sidebar.selectbox(
        "Drawing Tool",
        ["freedraw", "line", "rect", "circle", "transform"],
        key="drawing_mode"
    )

    # Clear button
    if st.sidebar.button("🗑️ Clear Canvas"):
        st.session_state.canvas_key = st.session_state.get('canvas_key', 0) + 1
        st.rerun()

    return {
        'stroke_width': stroke_width,
        'stroke_color': stroke_color,
        'bg_color': bg_color,
        'drawing_mode': drawing_mode
    }