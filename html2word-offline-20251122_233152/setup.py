from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="html2word",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful HTML to Word (.docx) converter with CSS style preservation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xupai2022/html2word",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "beautifulsoup4>=4.12.0",
        "python-docx>=1.1.0",
        "lxml>=5.0.0",
        "tinycss2>=1.2.0",
        "Pillow>=10.0.0",
        "requests>=2.31.0",
        "PyYAML>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "html2word=html2word.cli:main",
        ],
    },
)
