import subprocess
import os
import platform

def convert_to_pdf(input_path, output_path=None):
    """
    Converts a Word (.docx) file to PDF using LibreOffice on macOS or Linux.

    :param input_path: Path to the input .docx file
    :param output_path: Optional path to save the .pdf file
    :return: Path to the converted PDF
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Default output path
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".pdf"

    # Detect OS and set LibreOffice command path
    system = platform.system().lower()
    if system == "darwin":  # macOS
        soffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    elif system == "linux":
        soffice_path = "libreoffice"
    else:
        raise EnvironmentError("Unsupported OS — only macOS and Linux are supported.")

    # Ensure LibreOffice is installed
    try:
        subprocess.run([soffice_path, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise EnvironmentError("LibreOffice not found. Please install it first.")

    # Convert the file
    subprocess.run([
        soffice_path,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", os.path.dirname(output_path) or ".",
        input_path
    ], check=True)

    print(f"✅ PDF successfully created: {output_path}")
    return output_path

