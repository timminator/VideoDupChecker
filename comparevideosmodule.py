import os
import subprocess
import shutil
import winreg


def find_mkvextract():
    """
    Locates the `mkvextract` executable by checking the specific registry key for MKVToolnix.
    Extracts the path from the `UninstallString` if the key exists.
    Falls back to checking the current working directory.

    Returns:
        str: Full path to `mkvextract` if found, otherwise None.
    """
    try:
        # Open the specific registry key for MKVToolnix
        reg_path = os.path.join("SOFTWARE", "WOW6432Node", "Microsoft", "Windows", "CurrentVersion", "Uninstall", "MKVToolNix")
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            # Get the value of UninstallString
            uninstall_string = winreg.QueryValueEx(key, "UninstallString")[0]
            # Extract the installation directory
            install_path = os.path.dirname(uninstall_string)
            mkvextract_path = os.path.join(install_path, "mkvextract.exe")
            # Check if the file exists
            if os.path.exists(mkvextract_path):
                return mkvextract_path
    except FileNotFoundError:
        pass

    # Fallback: Check the current working directory
    mkvextract_path = os.path.join(os.getcwd(), "mkvextract.exe")
    if os.path.exists(mkvextract_path):
        return mkvextract_path

    # If not found, return None
    return None


def extract_video_tracks(input_folder, temp_folder, mode):
    """
    Extracts video tracks from MKV files using mkvextract.

    Args:
        input_folder (str): Path to the folder containing MKV files.
        temp_folder (str): Path to the folder for storing extracted video tracks.
        mode (str): Mode for extracting video tracks ("check_extras_folder", "check_movie_folder", "check_folder").

    Raises:
        FileNotFoundError: If mkvextract is not found.
    """
    mkvextract_path = find_mkvextract()
    if not mkvextract_path:
        raise FileNotFoundError(
            "Could not find 'mkvextract'. Please ensure it is installed with MKVToolnix or present in the same directory as this program."
        )

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    if mode == "check_extras_folder":
        # Process files only in the Extras folder
        for file in os.listdir(input_folder):
            if file.endswith(".mkv"):
                input_file = os.path.join(input_folder, file)
                output_file = os.path.join(temp_folder, f"{os.path.splitext(file)[0]}.h264")
                
                # Run mkvextract
                try:
                    subprocess.run([mkvextract_path, "tracks", input_file, f"0:{output_file}"], check=True)
                    print(f"Extracted video track from {file} to {output_file}")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to extract video track from {file}: {e}")

    elif mode == "check_movie_folder" or mode == "check_folder":
        # Process all .mkv files in the folder (including subfolders in check_movie_folder)
        for root, _, files in os.walk(input_folder):
            for file in files:
                if file.endswith(".mkv"):
                    input_file = os.path.join(root, file)
                    output_file = os.path.join(temp_folder, f"{os.path.splitext(file)[0]}.h264")
                    
                    # Run mkvextract
                    try:
                        subprocess.run([mkvextract_path, "tracks", input_file, f"0:{output_file}"], check=True)
                        print(f"Extracted video track from {file} to {output_file}")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to extract video track from {file}: {e}")


def trim_header_and_footer_for_folder(folder_path, header_size, footer_size):
    """
    Trims the header and footer of all files in the specified folder and appends '_trimmed' to their filenames.
    Deletes the original files after creating the trimmed versions.
    
    Args:
        folder_path (str): Path to the folder containing the files.
        header_size (int): Number of bytes to trim from the header.
        footer_size (int): Number of bytes to trim from the footer.
    """
    for filename in os.listdir(folder_path):
        input_file = os.path.join(folder_path, filename)
        
        # Skip directories and only process files
        if os.path.isfile(input_file):
            # Generate the output filename with '_trimmed'
            name, ext = os.path.splitext(filename)
            output_file = os.path.join(folder_path, f"{name}_trimmed{ext}")
            
            # Open the input file and calculate sizes
            with open(input_file, "rb") as f_in:
                file_size = f_in.seek(0, 2)  # Move to the end of the file to get its size
                keep_size = max(0, file_size - header_size - footer_size)  # Calculate size to retain
                
                # Ensure valid trimming
                if keep_size <= 0:
                    print(f"File {filename} is too small to trim both header and footer. Skipping.")
                    continue
                
                f_in.seek(header_size)  # Skip the header
                
                # Write the trimmed data to the new file
                with open(output_file, "wb") as f_out:
                    f_out.write(f_in.read(keep_size))  # Read and write the valid range
            
            # Delete the original file
            os.remove(input_file)
            print(f"Processed file: {input_file}")


def check_subsequence_with_stop_and_percentage_simple(small_file, large_file, threshold):
    """
    Checks if `small_file` is a subsequence of `large_file` with primitive 3-part comparison.
    Stops searching if a full match or significant partial match (> threshold%) is found.

    Args:
        small_file: Path to the smaller video file.
        large_file: Path to the larger video file.
        threshold (float): Percentage threshold for partial match.

    Returns:
        bool: True if match > threshold% or completely matched; False otherwise.
    """
    with open(small_file, 'rb') as sf, open(large_file, 'rb') as lf:
        # Read the entire smaller and larger files
        small_data = sf.read()
        large_data = lf.read()

        small_len = len(small_data)

        # Check the whole smaller file against the larger file
        if small_data in large_data:
            print("The smaller video stream is completely part of the larger video stream.")
            return True

        # Define threshold length for partial checks
        partial_len = int(small_len * (threshold / 100))

        # Check the first threshold% of the smaller file
        first_partial_data = small_data[:partial_len]
        if first_partial_data in large_data:
            print(f"The first {threshold}% of the smaller video stream matched the larger video stream.")
            return True

        # Check the last threshold% of the smaller file
        last_partial_data = small_data[-partial_len:]
        if last_partial_data in large_data:
            print(f"The last {threshold}% of the smaller video stream matched the larger video stream.")
            return True

        # If none of the checks matched
        print("No match found.")
        return False


def compare_videos(folder_path, threshold):
    """
    Compares each video file in the specified folder against others using the subsequence check function.
    Skips further comparisons for a file if it matches > threshold% with any other file.
    
    Args:
        folder_path (str): Path to the folder containing the video files.
        threshold (float): Percentage threshold for considering partial matches.
    
    Returns:
        list: Matches found in the folder.
    """
    # Get all video files in the folder
    video_files = [
        os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))
    ]

    # Retrieve file sizes for comparison logic
    video_files_with_sizes = [(file, os.path.getsize(file)) for file in video_files]
    
    # Sort the files by size in descending order
    video_files_with_sizes.sort(key=lambda x: x[1], reverse=True)

    # Calculate the total number of comparisons
    total_comparisons = sum(i for i in range(len(video_files_with_sizes)))

    current_comparison = 1
    matches = []  # Store successful matches

    # Compare each file to every other larger file
    for i, (small_file, small_size) in enumerate(video_files_with_sizes):
        for j, (large_file, large_size) in enumerate(video_files_with_sizes):
            if i <= j:  # Skip comparisons with the same or smaller files
                continue

            # Format filenames without "_trimmed.h264"
            small_file_display = os.path.basename(small_file).replace("_trimmed.h264", "")
            large_file_display = os.path.basename(large_file).replace("_trimmed.h264", "")
            
            # Convert sizes to MB and format
            small_size_mb = round(small_size / (1024 * 1024), 2)
            large_size_mb = round(large_size / (1024 * 1024), 2)

            print(f"Comparison {current_comparison} of {total_comparisons}:")
            print(f"Comparing {small_file_display} (size: {small_size_mb} MB) "
                  f"to {large_file_display} (size: {large_size_mb} MB)...")

            should_skip = check_subsequence_with_stop_and_percentage_simple(
                small_file, large_file, threshold
            )

            if should_skip:
                print(f"Skipping further comparisons for {small_file_display} due to (high) match.")
                matches.append((small_file_display, large_file_display))
                remaining_comparisons = len(video_files_with_sizes[:i]) - j
                current_comparison += remaining_comparisons
                break

            current_comparison += 1

    # Return matches at the end of the function
    return matches


def clear_temp_folder(temp_folder_path):
    """Clears all files in the temp folder."""
    if os.path.exists(temp_folder_path):
        for filename in os.listdir(temp_folder_path):
            file_path = os.path.join(temp_folder_path, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove directories
            else:
                os.remove(file_path)  # Remove files


def process_folder(folder_path, mode, threshold):
    """
    Processes a folder by extracting video tracks, trimming headers and footers, 
    and comparing videos for matches.

    Args:
        folder_path (str): Path to the folder to process.
        mode (str): Mode of operation, passed to `extract_video_tracks`.
        threshold (float): Percentage threshold for comparison.

    Returns:
        list: Matches found in the folder.
    """
    # Define the temp folder path relative to the program's location
    program_directory = os.path.dirname(os.path.abspath(__file__))
    temp_folder_path = os.path.join(program_directory, "temp")

    # Clear the temp folder at the beginning if it exists
    clear_temp_folder(temp_folder_path)

    # Create the temp folder if it doesn't exist
    os.makedirs(temp_folder_path, exist_ok=True)

    # Parameters
    header_size = 1024 * 1024   # Trims 1 MB from all files in the beginning
    footer_size = 1024 * 1024  # Trims 1 MB from all files in the end

    print(f"Extracting video tracks from {folder_path}...")
    try:
        extract_video_tracks(folder_path, temp_folder_path, mode)
    except FileNotFoundError as e:
            raise e from None
    else:
        print(f"Trimming headers and footers for files in {temp_folder_path}...")
        trim_header_and_footer_for_folder(temp_folder_path, header_size, footer_size)

        print(f"Comparing videos in {temp_folder_path}...")
        matches = compare_videos(temp_folder_path, threshold)
        
        # Clear the temp folder after processing
        clear_temp_folder(temp_folder_path)
        
        return matches
    finally:
        # Ensure temp folder is always removed, even if an error occurs
        shutil.rmtree(temp_folder_path, ignore_errors=True)  # Remove the temp folder itself
