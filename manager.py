import zipfile
import shutil
from pathlib import Path

# ===== CONFIG =====
new_folder_name = "MyProject"
new_tex_name = "main.tex"


def extract_and_rename(zip_path: Path, new_folder_name: str, new_tex_name: str) -> Path:
    extract_root = zip_path.parent

    temp_extract = extract_root / "__temp_extract__"

    if temp_extract.exists():
        shutil.rmtree(temp_extract)

    temp_extract.mkdir()

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)

        items = list(temp_extract.iterdir())

        if len(items) != 1 or not items[0].is_dir():
            raise Exception("ZIP must contain exactly one folder")

        inner_folder = items[0]

        final_folder = extract_root / new_folder_name

        if final_folder.exists():
            shutil.rmtree(final_folder)

        shutil.move(str(inner_folder), str(final_folder))

        tex_files = list(final_folder.glob("*.tex"))

        if len(tex_files) != 1:
            raise Exception("Expected exactly one .tex file")

        old_tex = tex_files[0]
        new_tex = final_folder / new_tex_name

        old_tex.rename(new_tex)

        print("Done!")
        print(f"Folder renamed to: {final_folder}")
        print(f"TEX file renamed to: {new_tex}")
        return final_folder
    finally:
        if temp_extract.exists():
            shutil.rmtree(temp_extract)
