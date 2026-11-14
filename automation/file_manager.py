
import os
import shutil
from pathlib import Path


class FileManager:

    def __init__(self):

        self.home_directory = Path.home()

        self.allowed_directories = [
            self.home_directory / "Desktop",
            self.home_directory / "Documents",
            self.home_directory / "Downloads",
            self.home_directory / "Pictures",
            self.home_directory / "Videos"
        ]

    def _validate_path(self, path):

        try:

            target = Path(path).expanduser().resolve()

            for directory in self.allowed_directories:

                allowed = directory.resolve()

                if target == allowed or allowed in target.parents:
                    return target

            return None

        except (OSError, ValueError):
            return None

    def create_folder(self, path):

        target = self._validate_path(path)

        if target is None:
            return False

        try:
            target.mkdir(parents=True, exist_ok=False)
            return True

        except OSError:
            return False

    def create_file(self, path, content=""):

        target = self._validate_path(path)

        if target is None or target.exists():
            return False

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return True

        except OSError:
            return False

    def search_files(self, directory, filename):

        target = self._validate_path(directory)

        if target is None or not target.is_dir():
            return []

        if not isinstance(filename, str) or not filename.strip():
            return []

        results = []

        try:

            for root, dirs, files in os.walk(target):

                dirs[:] = [
                    directory for directory in dirs
                    if directory.lower() not in {
                        "system volume information",
                        "$recycle.bin"
                    }
                ]

                for file in files:

                    if filename.lower() in file.lower():
                        results.append(str(Path(root) / file))

        except OSError:
            pass

        return results

    def rename_file(self, old_path, new_path):

        source = self._validate_path(old_path)
        destination = self._validate_path(new_path)

        if source is None or destination is None:
            return False

        if not source.is_file() or destination.exists():
            return False

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.rename(destination)
            return True

        except OSError:
            return False

    def delete_file(self, path):

        target = self._validate_path(path)

        if target is None or not target.is_file():
            return False

        try:
            target.unlink()
            return True

        except OSError:
            return False

    def list_files(self, directory):

        target = self._validate_path(directory)

        if target is None or not target.is_dir():
            return []

        try:
            return [
                {
                    "name": item.name,
                    "path": str(item),
                    "type": "folder" if item.is_dir() else "file"
                }
                for item in target.iterdir()
            ]

        except OSError:
            return []
