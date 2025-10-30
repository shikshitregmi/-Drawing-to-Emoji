import streamlit as st
import base64
from PIL import Image
import numpy as np
import os
import sys

# Add utils to path
sys.path.append('utils')

from utils.emoji_matcher import EmojiMatcher
from utils.drawing_canvas import DrawingCanvas, render_drawing_controls
from utils.image_processor import ImageProcessor

# Page configuration
st.set_page_config(
    page_title="🎨 Draw to Emoji Magic",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load custom CSS
def load_css():
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


class DrawingToEmojiApp:
    def __init__(self):
        self.emoji_matcher = EmojiMatcher()
        self.drawing_canvas = DrawingCanvas()
        self.image_processor = ImageProcessor()
        load_css()

    def render_sidebar(self):
        """Render the sidebar with controls and information"""
        st.sidebar.title("🎨 Draw to Emoji")
        st.sidebar.markdown("---")

        # Drawing controls
        drawing_settings = render_drawing_controls()

        st.sidebar.markdown("---")
        st.sidebar.header("ℹ️ How to Use")
        st.sidebar.info("""
        1. **Draw** something in the canvas
        2. **Describe** your drawing in text
        3. Get **emoji suggestions**
        4. Click on emojis to use them!
        """)

        st.sidebar.markdown("---")
        st.sidebar.header("🎯 Quick Examples")
        examples = [
            "Happy face with smile",
            "Cat with whiskers",
            "Heart shape",
            "Pizza slice",
            "Sun with rays",
            "Tree with leaves"
        ]

        for example in examples:
            if st.sidebar.button(f"✨ {example}", key=f"ex_{example}"):
                st.session_state.text_input = example
                st.rerun()

        return drawing_settings

    def render_drawing_tab(self):
        """Render the drawing tab"""
        st.header("🎨 Draw Your Creation")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Drawing Canvas")
            # Create canvas with unique key for clearing functionality
            canvas_key = st.session_state.get('canvas_key', 0)
            canvas_result = self.drawing_canvas.render_canvas(key=f"canvas_{canvas_key}")

            # Image analysis
            if canvas_result.image_data is not None:
                image_data = self.drawing_canvas.get_image_data(canvas_result)
                pil_image = self.drawing_canvas.convert_to_pil_image(image_data)

                if pil_image:
                    # Analyze drawing features
                    image_array = np.array(pil_image)
                    features = self.image_processor.analyze_drawing_features(image_array)

                    if features.get('has_content'):
                        suggestion = self.image_processor.image_to_text_suggestion(features)
                        st.info(f"🤖 Drawing analysis suggests: **{suggestion}**")

        with col2:
            st.subheader("Drawing Description")
            text_input = st.text_area(
                "Describe what you drew:",
                value=st.session_state.get('text_input', ''),
                placeholder="e.g., A smiling face, a cute cat, a beautiful flower...",
                height=150,
                key="drawing_description"
            )

            if st.button("🎯 Find Matching Emojis", type="primary"):
                if text_input:
                    self.process_and_display_results(text_input)
                else:
                    st.warning("Please describe your drawing first!")

            st.markdown("---")
            st.subheader("💡 Tips")
            st.markdown("""
            - Be specific in your description
            - Mention colors and shapes
            - Describe emotions for faces
            - Include details like size or style
            """)

    def render_text_tab(self):
        """Render the text description tab"""
        st.header("📝 Describe Your Idea")

        col1, col2 = st.columns([1, 1])

        with col1:
            text_input = st.text_area(
                "Describe what you want to convert to emoji:",
                value=st.session_state.get('text_input', ''),
                placeholder="e.g., A happy face with heart eyes, a cute puppy playing, a delicious pizza with pepperoni...",
                height=200,
                key="text_description"
            )

            if st.button("🔍 Find Emojis", type="primary"):
                if text_input:
                    self.process_and_display_results(text_input)
                else:
                    st.warning("Please enter a description first!")

        with col2:
            st.subheader("Categories")
            categories = self.emoji_matcher.get_all_categories()
            selected_category = st.selectbox("Browse by category:", ["All"] + categories)

            if selected_category != "All":
                category_emojis = self.emoji_matcher.get_emoji_by_category(selected_category)
                st.markdown(f"**{selected_category.title()} Emojis:**")
                emoji_display = " ".join(category_emojis[:10])
                st.markdown(f"<div style='font-size: 30px;'>{emoji_display}</div>", unsafe_allow_html=True)

    def render_search_tab(self):
        """Render the emoji search tab"""
        st.header("🔍 Emoji Search")

        col1, col2 = st.columns([2, 1])

        with col1:
            search_query = st.text_input(
                "Search for emojis by keyword:",
                placeholder="e.g., love, animal, food, happy..."
            )

            if search_query:
                matching_emojis = self.emoji_matcher.search_emojis(search_query)

                if matching_emojis:
                    st.success(f"Found {len(matching_emojis)} emojis matching '{search_query}'")

                    # Display emojis in grid
                    cols = st.columns(6)
                    for i, emoji in enumerate(matching_emojis[:18]):  # Show max 18 emojis
                        with cols[i % 6]:
                            emoji_info = self.emoji_matcher.get_emoji_info(emoji)
                            st.markdown(f"<div style='text-align: center;'>"
                                        f"<div style='font-size: 30px;'>{emoji}</div>"
                                        f"<small>{', '.join(emoji_info['keywords'][:2])}</small>"
                                        f"</div>", unsafe_allow_html=True)
                else:
                    st.warning(f"No emojis found matching '{search_query}'")

        with col2:
            st.subheader("Popular Searches")
            popular_searches = ["love", "happy", "animal", "food", "celebration", "travel"]
            for search in popular_searches:
                if st.button(f"🔍 {search.title()}", key=f"search_{search}"):
                    st.session_state.search_query = search
                    st.rerun()

    def process_and_display_results(self, text_input):
        """Process input and display emoji results"""
        with st.spinner("Finding the perfect emojis..."):
            # Get emoji matches
            matching_emojis = self.emoji_matcher.text_to_emoji(text_input, top_k=8)

            if matching_emojis:
                self.display_emoji_results(text_input, matching_emojis)
            else:
                st.error("No matching emojis found. Try a different description.")

    def display_emoji_results(self, text_input, matching_emojis):
        """Display the emoji matching results"""
        st.markdown("---")
        st.header("🎯 Matching Emojis")

        # Best match
        if matching_emojis:
            best_match = matching_emojis[0]
            best_info = self.emoji_matcher.get_emoji_info(best_match)

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                st.markdown("<div class='emoji-result'>", unsafe_allow_html=True)
                st.markdown(f"<div class='emoji-display'>{best_match}</div>", unsafe_allow_html=True)
                st.markdown(f"### Best Match")
                st.markdown(f"**Keywords:** {', '.join(best_info['keywords'][:5])}")
                st.markdown(f"**Category:** {best_info['category'].title()}")
                st.markdown("</div>", unsafe_allow_html=True)

            # Similar suggestions
            st.subheader("Similar Suggestions")
            cols = st.columns(8)
            for i, emoji in enumerate(matching_emojis[1:]):
                if i < 7:  # Show up to 7 suggestions
                    with cols[i]:
                        emoji_info = self.emoji_matcher.get_emoji_info(emoji)
                        st.markdown(
                            f"<div style='text-align: center; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;'>"
                            f"<div class='suggestion-emoji'>{emoji}</div>"
                            f"<small>{emoji_info['category'].title()}</small>"
                            f"</div>", unsafe_allow_html=True)

            # Copy to clipboard functionality
            st.markdown("---")
            st.subheader("📋 Copy Emojis")
            emoji_string = " ".join(matching_emojis[:5])
            st.code(emoji_string, language="")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copy Top 5 Emojis"):
                    st.success("Emojis copied to clipboard! (In a real app, this would use pyperclip)")

            with col2:
                if st.button("🔄 New Search"):
                    st.session_state.text_input = ""
                    st.rerun()

    def run(self):
        """Main application runner"""
        # Initialize session state
        if 'text_input' not in st.session_state:
            st.session_state.text_input = ""

        # Render sidebar
        self.render_sidebar()

        # Main content
        st.title("🎨 Draw to Emoji Magic")
        st.markdown("Transform your drawings and ideas into perfect emojis!")

        # Create tabs
        tab1, tab2, tab3 = st.tabs(["🎨 Draw", "📝 Describe", "🔍 Search"])

        with tab1:
            self.render_drawing_tab()

        with tab2:
            self.render_text_tab()

        with tab3:
            self.render_search_tab()

        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666;'>"
            "Made with ❤️ using Streamlit | Draw to Emoji Magic v1.0"
            "</div>",
            unsafe_allow_html=True
        )


def main():
    # Check if required files exist
    if not os.path.exists("assets/emoji_database.json"):
        st.error("❌ Emoji database not found. Please make sure 'assets/emoji_database.json' exists.")
        return

    # Initialize and run the app
    app = DrawingToEmojiApp()
    app.run()


if __name__ == "__main__":
    main()