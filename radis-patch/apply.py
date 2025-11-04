# Radis patch script
# Radis version: 0.16.2
import os
import shutil
import sys
from pathlib import Path

# Check if running on Windows or Linux/MacOS
WINDOWS = "nt" # Windows
POSIX = "posix" # Linux/MacOS
OS = os.name

# Get python packages path depending on OS
radis_path = ""
vaex_path = ""
if OS == WINDOWS:
    radis_path = "..\\.venv\\Lib\\site-packages\\radis\\"
    vaex_path = "..\\.venv\\Lib\\site-packages\\vaex\\"
elif OS == POSIX:
    radis_path = "../.venv/lib/python3.12/site-packages/radis/"
    vaex_path = "../.venv/lib/python3.12/site-packages/vaex/"
else:
    print(f"Unknown OS: {OS}.")
    sys.exit(1)

# The source directory is the directory containing this script
SOURCE_DIR = Path(__file__).resolve().parent
DEST_DIR_RADIS_LBL = SOURCE_DIR / f"{radis_path}lbl"
DEST_DIR_RADIS_API = SOURCE_DIR / f"{radis_path}api"
DEST_DIR_VAEX_HDF5 = SOURCE_DIR / f"{vaex_path}hdf5"

RADIS_LBL_FILES = ["base.py", "broadening.py", "loader.py"]
RADIS_API_FILES = ["dbmanager.py", "tools.py", "hdf5.py"]
VAEX_HDF5_FILES = ["utils.py"]

# Resolve destination directories
DEST_DIR_RADIS_LBL = DEST_DIR_RADIS_LBL.resolve()
DEST_DIR_RADIS_API = DEST_DIR_RADIS_API.resolve()
DEST_DIR_VAEX_HDF5 = DEST_DIR_VAEX_HDF5.resolve()

# Exit if the destination directories do not exist
if not DEST_DIR_RADIS_LBL.is_dir():
    print(f"Destination directory for radis/lbl does not exist: {DEST_DIR_RADIS_LBL}")
    print("Have you created the virtual environment and installed radis?")
    sys.exit(1)

if not DEST_DIR_RADIS_API.is_dir():
    print(f"Destination directory for radis/api does not exist: {DEST_DIR_RADIS_API}")
    print("Have you created the virtual environment and installed radis?")
    sys.exit(1)

if not DEST_DIR_VAEX_HDF5.is_dir():
    print(f"Destination directory for vaex/hdf5 does not exist: {DEST_DIR_VAEX_HDF5}")
    print("Have you created the virtual environment and installed vaex?")
    sys.exit(1)

# Move the files from the source to the destination
for file in RADIS_LBL_FILES:
    src_file = SOURCE_DIR / file
    if src_file.is_file():
        shutil.copy(src_file, DEST_DIR_RADIS_LBL)
        print(f"Moved {file} to {DEST_DIR_RADIS_LBL}")
    else:
        print(f"File {file} does not exist in the source directory.")

for file in RADIS_API_FILES:
    src_file = SOURCE_DIR / file
    if src_file.is_file():
        shutil.copy(src_file, DEST_DIR_RADIS_API)
        print(f"Moved {file} to {DEST_DIR_RADIS_API}")
    else:
        print(f"File {file} does not exist in the source directory.")

for file in VAEX_HDF5_FILES:
    src_file = SOURCE_DIR / file
    if src_file.is_file():
        shutil.copy(src_file, DEST_DIR_VAEX_HDF5)
        print(f"Moved {file} to {DEST_DIR_VAEX_HDF5}")
    else:
        print(f"File {file} does not exist in the source directory.")

# Print a success message
print("Radis patch applied successfully.")
