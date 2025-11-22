"""
Image processing utilities.

Handles downloading, decoding, format conversion, and sizing of images.
"""

import os
import base64
import io
import logging
from typing import Optional, Tuple, Union
from urllib.parse import urlparse, urljoin
import requests
from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processor for handling images from various sources."""

    # Word-supported image formats
    SUPPORTED_FORMATS = {"PNG", "JPEG", "JPG", "GIF", "BMP", "TIFF"}

    # Download timeout in seconds
    DOWNLOAD_TIMEOUT = 10

    # Maximum image size (width or height) in pixels
    MAX_IMAGE_SIZE = 4000

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize image processor.

        Args:
            base_path: Base path for resolving relative image paths
        """
        self.base_path = base_path or os.getcwd()

    def process_image(
        self,
        src: str,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        transform: Optional[str] = None,
        filter_css: Optional[str] = None
    ) -> Optional[Tuple[io.BytesIO, Tuple[int, int]]]:
        """
        Process an image from any source.

        Args:
            src: Image source (local path, URL, or base64 data URI)
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            transform: CSS transform value (e.g., "rotate(15deg)")
            filter_css: CSS filter value (e.g., "grayscale(100%)")

        Returns:
            Tuple of (image_stream, (width, height)) or None if failed
        """
        try:
            # Get image from source
            image = self._load_image(src)
            if image is None:
                return None

            # Convert to supported format if needed
            image = self._ensure_supported_format(image)

            # Apply CSS filters if specified
            if filter_css:
                image = self._apply_css_filters(image, filter_css)

            # Apply CSS transforms if specified
            if transform:
                image = self._apply_css_transform(image, transform)

            # Resize if needed
            if max_width or max_height:
                image = self._resize_image(image, max_width, max_height)

            # Limit size to prevent huge images
            image = self._limit_size(image)

            # Convert to BytesIO stream
            stream = io.BytesIO()
            image_format = image.format or "PNG"

            # Convert RGBA to RGB for JPEG
            if image_format == "JPEG" and image.mode == "RGBA":
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                image = rgb_image

            image.save(stream, format=image_format)
            stream.seek(0)

            return stream, image.size

        except Exception as e:
            logger.error(f"Error processing image '{src}': {e}")
            return None

    def _load_image(self, src: str) -> Optional[Image.Image]:
        """
        Load image from source.

        Args:
            src: Image source

        Returns:
            PIL Image object or None
        """
        # Check if it's a data URI (base64)
        if src.startswith("data:"):
            return self._load_from_data_uri(src)

        # Check if it's a URL
        if self._is_url(src):
            return self._load_from_url(src)

        # Assume it's a local file path
        return self._load_from_file(src)

    def _load_from_data_uri(self, data_uri: str) -> Optional[Image.Image]:
        """Load image from base64 data URI."""
        try:
            # Format: data:image/png;base64,iVBORw0KG...
            if ";base64," not in data_uri:
                logger.error("Invalid data URI format")
                return None

            header, base64_data = data_uri.split(";base64,", 1)
            image_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_data))
            logger.debug(f"Loaded image from data URI ({image.format}, {image.size})")
            return image

        except Exception as e:
            logger.error(f"Error loading image from data URI: {e}")
            return None

    def _load_from_url(self, url: str) -> Optional[Image.Image]:
        """Load image from URL."""
        try:
            response = requests.get(url, timeout=self.DOWNLOAD_TIMEOUT)
            response.raise_for_status()

            image = Image.open(io.BytesIO(response.content))
            logger.debug(f"Downloaded image from {url} ({image.format}, {image.size})")
            return image

        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None

    def _load_from_file(self, file_path: str) -> Optional[Image.Image]:
        """Load image from local file."""
        try:
            # Resolve relative paths
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.base_path, file_path)

            if not os.path.exists(file_path):
                logger.error(f"Image file not found: {file_path}")
                return None

            image = Image.open(file_path)
            logger.debug(f"Loaded image from {file_path} ({image.format}, {image.size})")
            return image

        except Exception as e:
            logger.error(f"Error loading image from {file_path}: {e}")
            return None

    def _is_url(self, src: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(src)
            return result.scheme in ("http", "https")
        except:
            return False

    def _ensure_supported_format(self, image: Image.Image) -> Image.Image:
        """
        Ensure image is in a Word-supported format.

        Args:
            image: PIL Image

        Returns:
            Converted image if needed
        """
        if image.format and image.format.upper() in self.SUPPORTED_FORMATS:
            return image

        # Convert unsupported formats (e.g., WebP, SVG) to PNG
        logger.debug(f"Converting image from {image.format} to PNG")
        converted = Image.new("RGBA", image.size)
        converted.paste(image)
        converted.format = "PNG"
        return converted

    def _resize_image(
        self,
        image: Image.Image,
        max_width: Optional[int],
        max_height: Optional[int]
    ) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.

        Args:
            image: PIL Image
            max_width: Maximum width
            max_height: Maximum height

        Returns:
            Resized image
        """
        width, height = image.size

        # Calculate scaling factor
        scale_w = max_width / width if max_width and width > max_width else 1.0
        scale_h = max_height / height if max_height and height > max_height else 1.0
        scale = min(scale_w, scale_h)

        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            logger.debug(f"Resizing image from {image.size} to ({new_width}, {new_height})")
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return image

    def _limit_size(self, image: Image.Image) -> Image.Image:
        """
        Limit image size to prevent huge images.

        Args:
            image: PIL Image

        Returns:
            Resized image if needed
        """
        width, height = image.size
        if width > self.MAX_IMAGE_SIZE or height > self.MAX_IMAGE_SIZE:
            return self._resize_image(image, self.MAX_IMAGE_SIZE, self.MAX_IMAGE_SIZE)
        return image

    def calculate_display_size(
        self,
        image_size: Tuple[int, int],
        css_width: Optional[str] = None,
        css_height: Optional[str] = None,
        max_width: Optional[float] = None,
        max_height: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Calculate display size for image in inches (for Word).

        Args:
            image_size: Original image size (width, height) in pixels
            css_width: CSS width value
            css_height: CSS height value
            max_width: Maximum width in inches
            max_height: Maximum height in inches

        Returns:
            Display size (width, height) in inches
        """
        from html2word.utils.units import UnitConverter

        img_width, img_height = image_size
        aspect_ratio = img_width / img_height if img_height > 0 else 1.0

        # Default DPI for images
        dpi = 96
        default_width = img_width / dpi
        default_height = img_height / dpi

        # Parse CSS dimensions
        width_inches = None
        height_inches = None

        if css_width:
            width_pt = UnitConverter.to_pt(css_width)
            width_inches = width_pt / 72

        if css_height:
            height_pt = UnitConverter.to_pt(css_height)
            height_inches = height_pt / 72

        # Calculate final dimensions
        if width_inches and height_inches:
            # Both specified
            final_width = width_inches
            final_height = height_inches
        elif width_inches:
            # Only width specified
            final_width = width_inches
            final_height = width_inches / aspect_ratio
        elif height_inches:
            # Only height specified
            final_height = height_inches
            final_width = height_inches * aspect_ratio
        else:
            # Neither specified, use default
            final_width = default_width
            final_height = default_height

        # Apply max constraints
        if max_width and final_width > max_width:
            final_width = max_width
            final_height = max_width / aspect_ratio

        if max_height and final_height > max_height:
            final_height = max_height
            final_width = max_height * aspect_ratio

        return final_width, final_height

    def _apply_css_filters(self, image: Image.Image, filter_css: str) -> Image.Image:
        """
        Apply CSS filters to image using PIL.

        Supports: grayscale, brightness, contrast, blur, sepia (partial support).

        Args:
            image: PIL Image
            filter_css: CSS filter value (e.g., "grayscale(100%) brightness(150%)")

        Returns:
            Filtered image
        """
        try:
            from PIL import ImageEnhance, ImageFilter
            import re

            # Parse multiple filters
            filter_pattern = r'(\w+)\(([^)]+)\)'
            matches = re.findall(filter_pattern, filter_css)

            for filter_name, filter_value in matches:
                filter_name = filter_name.lower()

                if filter_name == 'grayscale':
                    # Extract percentage (0-100%)
                    percent = self._parse_percentage(filter_value)
                    if percent > 0:
                        # Convert to grayscale
                        gray = image.convert('L')
                        # Blend with original based on percentage
                        if percent < 100:
                            image = Image.blend(image.convert('RGB'), gray.convert('RGB'), percent / 100.0)
                        else:
                            image = gray.convert('RGB')
                        logger.debug(f"Applied grayscale({percent}%)")

                elif filter_name == 'brightness':
                    # Extract percentage or decimal
                    factor = self._parse_filter_factor(filter_value, default=1.0)
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(factor)
                    logger.debug(f"Applied brightness({factor})")

                elif filter_name == 'contrast':
                    factor = self._parse_filter_factor(filter_value, default=1.0)
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(factor)
                    logger.debug(f"Applied contrast({factor})")

                elif filter_name == 'blur':
                    # Extract pixel radius
                    match = re.search(r'([\d.]+)px', filter_value)
                    if match:
                        radius = float(match.group(1))
                        image = image.filter(ImageFilter.GaussianBlur(radius))
                        logger.debug(f"Applied blur({radius}px)")

                elif filter_name == 'sepia':
                    # Simplified sepia tone
                    percent = self._parse_percentage(filter_value)
                    if percent > 0:
                        # Convert to sepia (simplified)
                        image = image.convert('RGB')
                        pixels = image.load()
                        width, height = image.size
                        for y in range(height):
                            for x in range(width):
                                r, g, b = pixels[x, y]
                                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                                pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
                        logger.debug(f"Applied sepia({percent}%)")

            return image

        except Exception as e:
            logger.warning(f"Error applying CSS filters: {e}")
            return image  # Return original on error

    def _apply_css_transform(self, image: Image.Image, transform: str) -> Image.Image:
        """
        Apply CSS transform to image using PIL.

        Supports: rotate, scale (partial support for others).

        Args:
            image: PIL Image
            transform: CSS transform value (e.g., "rotate(15deg)")

        Returns:
            Transformed image
        """
        try:
            import re

            # Parse transform functions
            transform_pattern = r'(\w+)\(([^)]+)\)'
            matches = re.findall(transform_pattern, transform)

            for transform_name, transform_value in matches:
                transform_name = transform_name.lower()

                if transform_name == 'rotate':
                    # Extract angle
                    match = re.search(r'([-\d.]+)deg', transform_value)
                    if match:
                        angle = float(match.group(1))
                        # PIL rotates counter-clockwise, CSS clockwise
                        image = image.rotate(-angle, expand=True, fillcolor='white')
                        logger.debug(f"Applied rotate({angle}deg)")

                elif transform_name == 'scale':
                    # Extract scale factor
                    parts = transform_value.split(',')
                    if len(parts) == 2:
                        scale_x = float(parts[0].strip())
                        scale_y = float(parts[1].strip())
                    else:
                        scale_x = scale_y = float(transform_value.strip())

                    new_width = int(image.width * scale_x)
                    new_height = int(image.height * scale_y)
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logger.debug(f"Applied scale({scale_x}, {scale_y})")

                elif transform_name == 'skewx':
                    # Simplified skew (not fully accurate)
                    logger.warning(f"skewX transform not fully supported, skipping")

                elif transform_name == 'skewy':
                    logger.warning(f"skewY transform not fully supported, skipping")

            return image

        except Exception as e:
            logger.warning(f"Error applying CSS transform: {e}")
            return image  # Return original on error

    def _parse_percentage(self, value: str) -> float:
        """Parse percentage value (e.g., "100%", "0.5") to 0-100."""
        value = value.strip()
        if '%' in value:
            return float(value.replace('%', ''))
        else:
            # Assume decimal (0-1)
            return float(value) * 100

    def _parse_filter_factor(self, value: str, default: float = 1.0) -> float:
        """Parse filter factor (e.g., "150%", "1.5") to multiplier."""
        value = value.strip()
        if '%' in value:
            return float(value.replace('%', '')) / 100.0
        else:
            return float(value)
