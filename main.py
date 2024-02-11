import sys
import logging
from pathlib import Path

from file_organizer import FileOrganizer

def main():
    
    path_folder = Path(sys.argv[1])

    if (path_folder.exists() and
        path_folder.is_dir()):
        
        organizer = FileOrganizer(path_folder)
        organizer.start()
    else:
        print(f"The folder address is incorrect: ({path_folder})")
    


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(threadName)s %(message)s')
    main()