from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


DEFAULT_TEX_PATH = Path("output") / "MyProject" / "main.tex"

# Common Unicode math/text symbols that frequently appear in OCR output.
UNICODE_TO_LATEX = {
    "∴": r"$\\therefore$",
    "⇒": r"$\\Rightarrow$",
    "→": r"$\\to$",
    "≤": r"$\\leq$",
    "≥": r"$\\geq$",
    "×": r"$\\times$",
    "−": "-",
    "…": r"\\ldots{}",
}


def remove_declare_unicode_lines(tex_text: str) -> str:
    return re.sub(r"^\\DeclareUnicodeCharacter\{[^}]+\}\{.*\}\s*$", "", tex_text, flags=re.MULTILINE)


def replace_common_unicode_symbols(tex_text: str) -> str:
    for symbol, replacement in UNICODE_TO_LATEX.items():
        tex_text = tex_text.replace(symbol, replacement)
    return tex_text


def run_tectonic(tex_path: Path) -> None:
    subprocess.run(
        ["tectonic", tex_path.name],
        cwd=str(tex_path.parent),
        check=True,
    )


def stage_supporting_assets(source_tex_path: Path, temp_dir: Path) -> None:
    source_images_dir = source_tex_path.parent / "images"
    temp_images_dir = temp_dir / "images"

    if source_images_dir.exists() and source_images_dir.is_dir():
        shutil.copytree(source_images_dir, temp_images_dir)


def compile_tex_to_pdf(tex_path: Path) -> Path:
    if not tex_path.exists():
        raise FileNotFoundError(f"TeX file not found: {tex_path}")

    if shutil.which("tectonic") is None:
        raise RuntimeError("tectonic is not installed or not available on PATH")

    source_text = tex_path.read_text(encoding="utf-8")
    pass_builders = [
        ("raw", lambda text: text),
        ("no-unicode-declarations", remove_declare_unicode_lines),
        (
            "no-unicode-declarations-plus-symbol-normalization",
            lambda text: replace_common_unicode_symbols(remove_declare_unicode_lines(text)),
        ),
    ]

    last_error: subprocess.CalledProcessError | None = None

    for pass_name, build_text in pass_builders:
        candidate_text = build_text(source_text)

        with tempfile.TemporaryDirectory(dir=tex_path.parent) as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_tex_path = temp_dir_path / tex_path.name
            temp_tex_path.write_text(candidate_text, encoding="utf-8")
            stage_supporting_assets(tex_path, temp_dir_path)

            try:
                run_tectonic(temp_tex_path)
            except subprocess.CalledProcessError as error:
                last_error = error
                print(f"Tectonic pass failed: {pass_name}")
                continue

            built_pdf_path = temp_tex_path.with_suffix(".pdf")
            if not built_pdf_path.exists():
                raise FileNotFoundError(f"Expected PDF was not created: {built_pdf_path}")

            pdf_path = tex_path.with_suffix(".pdf")
            shutil.copyfile(built_pdf_path, pdf_path)
            print(f"Tectonic pass succeeded: {pass_name}")
            return pdf_path

    if last_error is not None:
        raise last_error

    raise RuntimeError("No compile pass was executed")


def main() -> Path:
    tex_path = DEFAULT_TEX_PATH

    if len(sys.argv) > 1:
        tex_path = Path(sys.argv[1])

    pdf_path = compile_tex_to_pdf(tex_path)
    print(f"Saved PDF: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    main()