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
        max_height: Optional[int] = None
    ) -> Optional[Tuple[io.BytesIO, Tuple[int, int]]]:
        """
        Process an image from any source.

        Args:
            src: Image source (local path, URL, or base64 data URI)
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels

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
