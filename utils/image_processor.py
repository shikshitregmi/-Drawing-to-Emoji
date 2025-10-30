import cv2
import numpy as np
from PIL import Image
import io


class ImageProcessor:
    @staticmethod
    def analyze_drawing_features(image_array):
        """Analyze basic features of the drawing (simplified version)"""
        if image_array is None:
            return {}

        # Convert to grayscale if needed
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array

        # Basic image analysis
        features = {}

        # Check if image has content (not empty)
        features['has_content'] = np.mean(gray) < 240  # Assuming white background

        # Detect shapes (simplified)
        features['is_circular'] = ImageProcessor._detect_circularity(gray)
        features['has_lines'] = ImageProcessor._detect_lines(gray)
        features['is_filled'] = ImageProcessor._detect_filled_area(gray)

        return features

    @staticmethod
    def _detect_circularity(gray_image):
        """Detect if the drawing contains circular shapes"""
        # Simple circularity detection
        _, binary = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.7:  # Close to circle
                        return True
        return False

    @staticmethod
    def _detect_lines(gray_image):
        """Detect if the drawing contains straight lines"""
        edges = cv2.Canny(gray_image, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10)
        return lines is not None and len(lines) > 0

    @staticmethod
    def _detect_filled_area(gray_image):
        """Detect if there are filled areas in the drawing"""
        _, binary = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        filled_pixels = np.sum(binary == 0)  # Count black pixels
        total_pixels = gray_image.size
        fill_ratio = filled_pixels / total_pixels
        return fill_ratio > 0.1  # More than 10% filled

    @staticmethod
    def image_to_text_suggestion(image_features):
        """Convert image features to text suggestions"""
        suggestions = []

        if image_features.get('is_circular'):
            suggestions.extend(["circle", "round", "ball", "face", "sun"])

        if image_features.get('has_lines'):
            suggestions.extend(["line", "straight", "building", "stick figure"])

        if image_features.get('is_filled'):
            suggestions.extend(["filled", "solid", "colored"])

        return " ".join(suggestions) if suggestions else "drawing"