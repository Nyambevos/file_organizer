
import logging
from pathlib import Path
from threading import Thread
import shutil


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


    def start(self):
        
        logging.debug(f'Start sorting')
        self._r_sort(self.start_folder)
        [el.join() for el in self.threads]
        self._clean_folder()
        logging.debug(f'Finish sorted')


    def _r_sort(self, path_folder):
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


                thread = Thread(target=self._r_sort, args=(path,))
            else:
                thread = Thread(target=self._move_file, args=(path,))


            thread.start()
            self.threads.append(thread)

    def _move_file(self, path_file: Path):
        path_destination_folder: Path
        new_name_file: str
        new_path_file: Path

        logging.debug(f'Moving file: {path_file.name}')

        # Визначення кінцевої папки
        for key, value in self.TYPE_FILE.items():
            if path_file.suffix.lstrip(".").upper() in value:
                path_destination_folder = Path(self.start_folder, key)
                break
        else:
            path_destination_folder = Path(self.start_folder, 'other')
        
        # Створення кінцевої папки, якщо не існує
        if not path_destination_folder.exists():
            path_destination_folder.mkdir()

        

        # Нормалізація імені файла
        if not path_destination_folder.name == "other":
            new_name_file = self.normalize_name(path_file.stem)
        else:
            new_name_file = path_file.stem

        # Перевірка дублікатів
        count = 0

        while True:
            name = new_name_file
            new_path: Path
            
            if count:
                name = f"{new_name_file}_{count}"

            new_path = Path(path_destination_folder, f"{name}{path_file.suffix}")
            
            if new_path.exists():
                count += 1
                continue
            
            new_name_file = name
            break
        
        new_path_file = Path(path_destination_folder, f"{new_name_file}{path_file.suffix}")

        if path_destination_folder.name == "archives":
            try:
                shutil.unpack_archive(path_file, Path(path_destination_folder, new_name_file))
                path_file.unlink()
            except:
                shutil.move(path_file, Path(path_destination_folder.parent, "other", path_file.name))
        else:
            shutil.move(path_file, new_path_file)


    def normalize_name(self, last_name):
        """Normalize the input text by replacing non-alphanumeric characters with underscores
           and applying Cyrillic to Latin transliteration."""
        # Initialize an empty string to store the normalized text
        new_name = ""
        # Iterate through each character in the input text
        for char in last_name:
            # Replace non-alphanumeric characters with underscores, keep alphanumeric characters unchanged
            if not char.isalnum():
                new_name += "_"
            else:
                new_name += char
        # Use the translate method to apply additional character mapping for transliteration
        return new_name.translate(self.MAP)

    def _clean_folder(self):
        for path in self.start_folder.iterdir():
            if not path.name in self.TYPE_FILE:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    thread = FileOrganizer(Path("/Users/nuambevos/Downloads/folder"))
    thread.start()