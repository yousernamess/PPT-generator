from pathlib import Path

from mpxpy.mathpix_client import MathpixClient


input_file_path = Path("test questions.pdf")
output_dir = Path("output")
output_stem = input_file_path.stem


def main() -> None:
    if not input_file_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_file_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    client = MathpixClient(
        app_id="abhigyangurukul_01fc1d_7cd82a",
        app_key="7beeca0384c335680f651826f273bc9f4e3d4708b6d39afc50af1c7cb87d82fe",
    )

    pdf = client.pdf_new(
        file_path=str(input_file_path),
        # convert_to_md=True,
        convert_to_tex_zip=True,
    )

    completed = pdf.wait_until_complete(timeout=300)
    if not completed:
        raise TimeoutError("Mathpix conversion did not complete within 300 seconds")

    # md_path = output_dir / f"{output_stem}.md"
    tex_zip_path = output_dir / f"{output_stem}.zip"

    # saved_md = pdf.to_md_file(path=str(md_path))
    saved_tex_zip = pdf.to_tex_zip_file(path=str(tex_zip_path))

    # print(f"Saved markdown: {saved_md}")
    print(f"Saved TeX zip: {saved_tex_zip}")
    return tex_zip_path


if __name__ == "__main__":
    main()
