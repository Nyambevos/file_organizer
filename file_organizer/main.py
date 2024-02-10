
import shutil
import logging
from pathlib import Path
from threading import Thread
from time import time


class FileOrganizer:
    TYPE_FILE = {
        "images": ('JPEG', 'PNG', 'JPG', 'SVG'),
        "video": ('AVI', 'MP4', 'MOV', 'MKV'),
        "documents": ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
        "audio": ('MP3', 'OGG', 'WAV', 'AMR'),
        "archives": ('ZIP', 'GZ', 'TAR'),
        "other": ()
    }

    MAP = {
        ord('А'): 'A',      ord('а'): 'a',
        ord('Б'): 'B',      ord('б'): 'b',
        ord('В'): 'V',      ord('в'): 'v',
        ord('Г'): 'G',      ord('г'): 'g',
        ord('Ґ'): 'G',      ord('ґ'): 'g',
        ord('Д'): 'D',      ord('д'): 'd',
        ord('Е'): 'E',      ord('е'): 'e',
        ord('Є'): 'Ye',     ord('є'): 'ye',
        ord('Ё'): 'Yo',     ord('ё'): 'yo',
        ord('Ж'): 'Zh',     ord('ж'): 'zh',
        ord('З'): 'Z',      ord('з'): 'z',
        ord('И'): 'I',      ord('и'): 'i',
        ord('І'): 'I',      ord('і'): 'i',
        ord('Ї'): 'Yi',     ord('ї'): 'yi',
        ord('Й'): 'Y',      ord('й'): 'y',
        ord('К'): 'K',      ord('к'): 'k',
        ord('Л'): 'L',      ord('л'): 'l',
        ord('М'): 'M',      ord('м'): 'm',
        ord('Н'): 'N',      ord('н'): 'n',
        ord('О'): 'O',      ord('о'): 'o',
        ord('П'): 'P',      ord('п'): 'p',
        ord('Р'): 'R',      ord('р'): 'r',
        ord('С'): 'S',      ord('с'): 's',
        ord('Т'): 'T',      ord('т'): 't',
        ord('У'): 'U',      ord('у'): 'u',
        ord('Ф'): 'F',      ord('ф'): 'f',
        ord('Х'): 'Kh',     ord('х'): 'kh',
        ord('Ц'): 'Ts',     ord('ц'): 'ts',
        ord('Ч'): 'Ch',     ord('ч'): 'ch',
        ord('Ш'): 'Sh',     ord('ш'): 'sh',
        ord('Щ'): 'Shch',   ord('щ'): 'shch',
        ord('Ъ'): '',       ord('ъ'): '',
        ord('Ы'): 'Y',      ord('ы'): 'y',
        ord('Ь'): '',       ord('ь'): '',
        ord('Э'): 'E',      ord('э'): 'e',
        ord('Ю'): 'Yu',     ord('ю'): 'yu',
        ord('Я'): 'Ya',     ord('я'): 'ya'
        }

    def __init__(self, start_folder) -> None:
        self.start_folder = start_folder
        self.threads = []

    def start(self) -> None:
        logging.debug('Start sorting')
        start_time = time()

        self._scan_folder(self.start_folder)
        [el.join() for el in self.threads]

        self._clean_folder()

        finish_time = time()
        logging.debug(f'Finish sorted. Time: {finish_time-start_time}')

    def _scan_folder(self, path_folder: Path) -> None:
        """The function goes through the target folder.
        The found subfolders are recursively opened
        in a new folder for scanning. The found files
        are processed and moved to a new thread."""
        logging.debug(f'scanning folder: {path_folder.name}')

        thread: Thread

        for path in path_folder.iterdir():
            # Skip hidden files or folders (those starting with ".")
            if path.name[0] == ".":
                continue

            # Check if the current entry is a directory
            if path.is_dir():
                if (path.parent == self.start_folder and
                        path.name in self.TYPE_FILE):
                    continue
                thread = Thread(target=self._scan_folder, args=(path,))
            else:
                thread = Thread(target=self._move_file, args=(path,))

            thread.start()
            self.threads.append(thread)

    def _move_file(self, path_file: Path):
        """The function of moving a file"""
        logging.debug(f'Moving file: {path_file.name}')

        name_file = path_file.stem
        file_suffix = path_file.suffix
        # Define the destination folder
        type_file = (
            self._define_destination_folder(path_file))

        # Normalize file name
        if not type_file == "other":
            name_file = self.normalize_name(name_file)

        # Check for duplicates
        name_file = self._check_duplicates(
            path_file,
            type_file)

        if type_file == "archives":
            try:
                destination_folder = self._create_folder(type_file)

                shutil.unpack_archive(
                    path_file,
                    Path(destination_folder, name_file))
                path_file.unlink()
            except:
                destination_folder = self._create_folder("other")
                shutil.move(
                    path_file,
                    Path(destination_folder, path_file.name))
        else:
            destination_folder = self._create_folder(type_file)

            final_path_file = Path(
                destination_folder,
                f"{name_file + file_suffix}")

            shutil.move(path_file, final_path_file)

    def _create_folder(self, name_folder) -> Path:
        """Function creates folder
        if it does not exist"""
        destination_folder = Path(
            self.start_folder,
            name_folder)

        if not destination_folder.exists():
            destination_folder.mkdir()

        return destination_folder

    def _define_destination_folder(self, path_file: Path) -> str:
        """The function determines the final
        folder for the file"""
        for key, value in self.TYPE_FILE.items():
            if path_file.suffix.lstrip(".").upper() in value:
                return key
        else:
            return "other"

    def _check_duplicates(self,
                          path_file: Path,
                          type_file: Path):
        """The function checks whether files with
        this name exist in the target folder.
        If such a file already exists, a suffix
        is added to the file name."""
        count = 0

        while True:
            name = path_file.stem
            new_path: Path

            if count:
                name = f"{name}_{count}"

            new_path = Path(
                self.start_folder,
                type_file,
                f"{name}{path_file.suffix}")

            if new_path.exists():
                count += 1
                continue

            return name

    def normalize_name(self, last_name):
        """Normalize the input text by replacing
        non-alphanumeric characters with underscores
        and applying Cyrillic to Latin transliteration."""

        # Initialize an empty string to store the normalized text
        new_name = ""
        # Iterate through each character in the input text
        for char in last_name:
            # Replace non-alphanumeric characters
            # with underscores, keep alphanumeric
            # characters unchanged
            if not char.isalnum():
                new_name += "_"
            else:
                new_name += char
        # Use the translate method to apply additional
        # character mapping for transliteration
        return new_name.translate(self.MAP)

    def _clean_folder(self):
        """The function clears the folder"""
        for path in self.start_folder.iterdir():
            if path.name not in self.TYPE_FILE:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(threadName)s %(message)s')

    thread = FileOrganizer(Path("/Users/nuambevos/Downloads/folder"))
    thread.start()
