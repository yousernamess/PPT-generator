from pathlib import Path

from extractor import main as extract_tex_zip
from manager import extract_and_rename, new_folder_name, new_tex_name


def main() -> Path:
    zip_path = extract_tex_zip()
    if not isinstance(zip_path, Path):
        zip_path = Path(zip_path)

    return extract_and_rename(zip_path, new_folder_name, new_tex_name)


if __name__ == "__main__":
    main()