from comparevideosmodule import process_folder
import os
import time
import argparse
from collections import defaultdict


def process_folders(base_folder, mode, threshold):
    """
    Processes folders based on the selected mode.

    Args:
        base_folder (str): Base folder to process.
        mode (str): "check_extras_folder", "check_movie_folder", or "check_folder".
        threshold (float): The percentage threshold for considering partial matches.

    Returns:
        defaultdict: Matches grouped by folder.
    """
    all_matches = defaultdict(list)

    # For "check_extras_folder" and "check_movie_folder", subfolders are identical
    subfolders = [
        os.path.join(base_folder, subfolder)
        for subfolder in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, subfolder))
    ]

    # For "check_folder", the subfolders list will just contain the base_folder
    if mode == "check_folder":
        subfolders = [base_folder]

    total_folders = len(subfolders)

    for index, folder_path in enumerate(subfolders, start=1):
        print(f"\n\nProcessing folder: {folder_path} (Folder {index} of {total_folders})\n")

        try:
            if mode == "check_extras_folder":
                # Process all subdirectories in the folder
                subdirectories = [
                    os.path.join(folder_path, subdir)
                    for subdir in os.listdir(folder_path)
                    if os.path.isdir(os.path.join(folder_path, subdir))
                ]
                for sub_index, subdirectory in enumerate(subdirectories, start=1):
                    print(f"\n\nProcessing subdirectory: {subdirectory} (Subdirectory {sub_index} of {len(subdirectories)})\n")
                    matches = process_folder(subdirectory, mode, threshold)
                    if matches:
                        all_matches[subdirectory].extend(matches)
            elif mode == "check_movie_folder" or mode == "check_folder":
                # Process all video files in the given folder (and subfolders for check_movie_folder)
                matches = process_folder(folder_path, mode, threshold)
                if matches:
                    all_matches[folder_path].extend(matches)
        except FileNotFoundError as e:
            raise e from None

    return all_matches


def validate_threshold(value):
    """
    Validates that the provided threshold is a float between 0 and 100.
    """
    try:
        f_value = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid float.")
    if not (0 <= f_value <= 100):
        raise argparse.ArgumentTypeError(f"{value} is out of range. Must be between 0 and 100.")
    return f_value


def main():
    parser = argparse.ArgumentParser(
        description="Process video folders for duplicate detection and comparison.",
        formatter_class=argparse.RawTextHelpFormatter  # Preserve formatting in help text
    )
    parser.add_argument(
        "folder_path",
        type=str,
        help="Path to the folder to process."
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["check_folder", "check_extras_folder", "check_movie_folder"],
        required=True,
        help=(
            "Specifies the mode of operation:\n\n"
            "1. check_folder:\n"
            "   Compares all videos contained in this folder and all its subfolders for duplicates.\n\n"
            "2. check_extras_folder:\n"
            "   Scans for videos in subdirectories within the specified folder structure.\n"
            "   The program will go through each folder within the specified top-level directory\n"
            "   and process all subdirectories it finds.\n"
            "   Each subdirectory (e.g., 'Extras', 'BehinTheScenes', etc.) will be processed individually.\n"
            "   Example folder structure:\n\n"
            "       Movies\n"
            "       ├── Movie 1\n"
            "       │   ├── BehindtheScenes\n"
            "       │   └── Subdirectory2\n"
            "       ├── Movie 2\n"
            "       │   ├── Extras\n"
            "       │   └── DeletedScenes\n"
            "       └── Movie 3\n"
            "           ├── BonusContent\n"
            "           └── Interviews\n\n"
            "3. check_movie_folder:\n"
            "   Compares all videos directly within movie folders, including their subfolders.\n"
            "   The program will iterate through all subdirectories within the specified top-level\n"
            "   directory and process videos in each folder and its subfolders.\n"
            "   Example folder structure:\n\n"
            "       Movies\n"
            "       ├── Movie 1\n"
            "       │   ├── Video1.mkv\n"
            "       │   ├── Video2.mkv\n"
            "       │   └── Subfolder\n"
            "       ├── Movie 2\n"
            "       │   └── Video3.mkv\n"
            "       └── Movie 3\n"
            "           ├── Video4.mkv\n"
            "           └── Subfolder\n\n"
        ),
    )
    parser.add_argument(
        "--threshold",
        type=validate_threshold,
        default=95.0,
        help=(
            "Optional: Percentage threshold for considering partial matches (default: 95%%). "
            "The program checks if the first 95%% or the last 95%% of the video file matches with another file."
        )
    )
    
    args = parser.parse_args()

    start = time.time()

    try:
        all_matches = process_folders(args.folder_path, args.mode, args.threshold)
    except FileNotFoundError as e:
        # Print the error message from the exception raised in process_folder
        print(f"Error: {e}")
    else:
        if not all_matches:
            print("\n\nNo duplicates or matches found in any folder.\n")
        else:
            print("\n\nCombined Matches:")
            print("-------------------------\n")
            for folder, matches in all_matches.items():
                print(f"Matches found in {folder}:")
                for small, large in matches:
                    print(f"- {small} is part of or matches {large} by more than {args.threshold}%.")
                print()
    finally:
        end = time.time()
        print(f"Time elapsed: {end - start:.3f}s.")

if __name__ == "__main__":
    main()
