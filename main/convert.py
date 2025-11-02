import os
import platform
import subprocess
import shutil

def convert_to_pdf(input_path, output_path=None):
    """
    Converts a Word (.docx, .pptx, etc.) file to PDF using LibreOffice on macOS or Linux.

    :param input_path: Path to the input file (e.g., .docx or .pptx)
    :param output_path: Optional path to save the resulting PDF
    :return: Path to the converted PDF file
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Default output path
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".pdf"

    output_dir = os.path.dirname(output_path) or "."
    os.makedirs(output_dir, exist_ok=True)

    # Detect OS
    system = platform.system().lower()
    if system == "darwin":  # macOS
        soffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    elif system == "linux":
        soffice_path = "libreoffice"
    else:
        raise EnvironmentError("Unsupported OS — only macOS and Linux are supported.")

    # Verify LibreOffice installation
    try:
        subprocess.run([soffice_path, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        raise EnvironmentError("LibreOffice not found. Please install it first.")

    # Convert file to PDF (LibreOffice outputs to the specified directory)
    subprocess.run([
        soffice_path,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path
    ], check=True)

    # Figure out the actual generated PDF name
    generated_pdf = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    )

    # Rename/move if necessary
    if os.path.abspath(generated_pdf) != os.path.abspath(output_path):
        shutil.move(generated_pdf, output_path)

    print(f"✅ PDF successfully created: {output_path}")
    return output_path