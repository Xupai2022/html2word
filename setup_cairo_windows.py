"""
Setup Cairo Graphics for Windows - configures cairo for cairosvg
"""

import os
import sys
import zipfile
from pathlib import Path

def find_cairo_files():
    """Find cairo files in the current directory."""
    current_dir = Path(__file__).parent
    print(f"Searching for Cairo files in: {current_dir}")

    # Check for cairo-windows.zip
    cairo_zip = current_dir / "cairo-windows.zip"
    gtk_runtime = current_dir / "gtk-runtime.exe"

    if cairo_zip.exists():
        print(f"✓ Found cairo-windows.zip")
        return {"zip": str(cairo_zip), "gtk_runtime": str(gtk_runtime) if gtk_runtime.exists() else None}
    else:
        print(f"✗ cairo-windows.zip not found in {current_dir}")
        print("Please download cairo-windows.zip from:")
        print("  https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer")
        return None

def extract_cairo_zip(zip_path, target_dir):
    """Extract cairo zip file."""
    print(f"\nExtracting {zip_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        print(f"✓ Extracted to {target_dir}")
        return True
    except Exception as e:
        print(f"✗ Failed to extract: {e}")
        return False

def find_dll_paths(base_dir):
    """Find cairo DLL files in extracted directories."""
    base_path = Path(base_dir)
    dll_paths = []

    # Search common locations
    possible_paths = [
        base_path / "bin",
        base_path / "lib",
        base_path / "cairo" / "bin",
        base_path / "gtk" / "bin",
    ]

    for path in possible_paths:
        if path.exists():
            # Look for cairo.dll or libcairo-2.dll
            cairo_dlls = list(path.glob("cairo.dll")) + list(path.glob("libcairo-2.dll"))
            if cairo_dlls:
                dll_paths.append(str(path))
                print(f"  Found cairo DLL at: {path}")

    if dll_paths:
        return list(set(dll_paths))  # Remove duplicates
    else:
        return None

def add_to_path(directories):
    """Add directories to PATH environment variable."""
    current_path = os.environ.get("PATH", "")
    paths_added = 0

    print("\nUpdating PATH environment variable...")
    for directory in directories:
        if directory not in current_path:
            print(f"  Adding to PATH: {directory}")
            if paths_added == 0:
                os.environ["PATH"] = directory + os.pathsep + os.environ.get("PATH", "")
            else:
                os.environ["PATH"] = directory + os.pathsep + os.environ.get("PATH", "")
            paths_added += 1
        else:
            print(f"  Already in PATH: {directory}")

    return paths_added > 0

def test_cairo_import():
    """Test if cairo can be imported."""
    print("\nTesting Cairo import...")
    try:
        import cairo
        print(f"✓ Cairo Python bindings imported successfully: {cairo.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import cairo Python module: {e}")
        print("\nYou may need to install pygobject:")
        print("  pip install pycairo pygobject")
        return False

def install_pycairo():
    """Install pycairo (Python bindings for cairo)."""
    print("\nAttempting to install pycairo...")
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pycairo"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ pycairo installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install pycairo: {e}")
        print(f"Error output: {e.stderr}")
        return False

def test_cairosvg():
    """Test if cairosvg can be imported."""
    print("\nTesting cairosvg import...")
    try:
        import cairosvg
        print(f"✓ cairosvg imported successfully: {cairosvg.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import cairosvg: {e}")
        return False

def install_cairosvg():
    """Install cairosvg."""
    print("\nAttempting to install cairosvg...")
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "cairosvg"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ cairosvg installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install cairosvg: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("Cairo Graphics Setup for Windows")
    print("=" * 60)

    # Step 1: Find files
    files = find_cairo_files()
    if not files:
        print("\n❌ Setup aborted: Cairo files not found")
        sys.exit(1)

    # Step 2: Extract cairo-windows.zip
    current_dir = Path(__file__).parent
    extract_dir = current_dir / "cairo_install"
    extract_dir.mkdir(exist_ok=True)

    if not extract_cairo_zip(files["zip"], extract_dir):
        print("\n❌ Setup aborted: Failed to extract cairo")
        sys.exit(1)

    # Step 3: Find DLL paths
    dll_dirs = find_dll_paths(extract_dir)
    if not dll_dirs:
        print("\n❌ Could not find cairo DLLs in extracted files")
        print("   Please check the zip file contents manually")
        sys.exit(1)

    # Step 4: Add to PATH
    path_updated = add_to_path(dll_dirs)
    if path_updated:
        print("\n✓ PATH updated successfully")
        print(f"   Note: You'll need to restart your terminal/IDE for PATH changes to take full effect")
    else:
        print("\n✓ PATH already configured")

    # Step 5: Install Python packages
    print("\n" + "=" * 60)
    print("Installing Python Packages")
    print("=" * 60)

    # Install pycairo first
    pycairo_ok = install_pycairo()

    # Install cairosvg
    cairosvg_ok = install_cairosvg()

    if not (pycairo_ok and cairosvg_ok):
        print("\n⚠ Some Python packages failed to install")
        print("   Try running with: pip install pycairo cairosvg")

    # Step 6: Test imports
    print("\n" + "=" * 60)
    print("Testing Imports")
    print("=" * 60)

    cairo_ok = test_cairo_import()
    cairosvg_ok = test_cairosvg()

    # Summary
    print("\n" + "=" * 60)
    print("Setup Summary")
    print("=" * 60)
    print(f"Cairo DLLs: {'✅ Found and configured' if dll_dirs else '❌ Missing'}")
    print(f"Python cairo: {'✅ Working' if cairo_ok else '❌ Not working'}")
    print(f"cairosvg: {'✅ Working' if cairosvg_ok else '❌ Not working'}")

    if dll_dirs and cairosvg_ok:
        print("\n🎉 Setup completed successfully!")
        print("Your SVG conversion should now work.")
    else:
        print("\n⚠ Some components not working properly")
        print("See the error messages above for details")

if __name__ == "__main__":
    main()
