<p align="center">
  <h1 align="center">VideoDupChecker</h1>
  <p align="center">
    Check your video collection for duplicates!
    <br />
  </p>
</p>

<br>

## ℹ About

VideoDupChecker is a command line tool for detecting video duplicates in a folder structure and checks if a smaller video is part of a larger video stream. It also detects if a specified portion (more info further down below) of a video file matches another one in the given folder.

The program supports multiple modes for different use cases, including comparing videos across folders or within specific subfolders (such as "Extras").

## Features
- **Duplicate Detection**: Compare videos to identify duplicates based on file content.
- **Flexible Modes**: Check  a specific folder, focus on "Extras" or scan complete movie directories.
- **Customizable Threshold**: Adjust the match threshold to suit your needs (default is 95%).  
  
## Notes
- The tool only checks if the video stream of a file matches that of another one. There can still be differences in the audio tracks or included subtitles. This has to be checked before you can delete them safely.

## Requirements

- **Video format**: Your video files need to be in the MKV format.

- **MKVToolNix**: You need the `mkvextract.exe` tool for extracting video tracks. Either install MKVToolNix or place `mkvextract.exe` in the same directory as the `VideoDupChecker.exe` file.

- **RAM**: The program requires as much RAM as the combined size of the two largest video files being compared. Make sure your system has sufficient available memory to handle the file sizes, especially when working with large video files.

- **Temporary Storage**: The program requires temporary storage to process the video files. It will create a temp folder in the directory you are executing the program in.  
The storage requirements depend on the mode you are running (further down you will find more info about them):
  - In `check_folder` mode: You will need temporary storage for the entire contents of the folder being processed.
  - In `check_extras_folder` mode: You will need temporary storage for the largest `Extras` subfolder.
  - In `check_movie_folder` mode: You will need temporary storage for the largest `movie` folder (including subfolders).
  
  Ensure you have enough space in the directory where you execute the program. The program will automatically clean up the temporary files after processing.


## Usage

### Command-Line Arguments

The program is run via the terminal with the following arguments:

```
VideoDupChecker.exe <folder_path> --mode <mode> [--threshold <percentage>]  
```
<br/>

The arguments are as follows:

- **folder_path**: Path to the folder you want to process.
- **--mode**: Specifies the mode of operation.
  - `check_folder`: Compares all videos contained in this folder and all its subfolders for duplicates.
  - `check_extras_folder`: Looks specifically for videos in 'Extras' subfolders within the specified folder    structure. The program will scan each folder within the specified top-level directory and process any      'Extras' subfolders it finds.
    An example folder structure for this case:
    
           Movies
           ├── Movie 1
           │   └── Extras
           ├── Movie 2
           │   └── Extras
           └── Movie 3
               └── Extras
  
  - `check_movie_folder`:  Compares all videos directly within movie folders, including their subfolders.
    The program will iterate through all subdirectories within the specified top-level
    directory and process videos in each folder and its subfolders.
    An example folder structure for this case:

           Movies
           ├── Movie 1
           │   ├── Video1.mkv
           │   ├── Video2.mkv
           │   └── Subfolder
           ├── Movie 2
           │   └── Video3.mkv
           └── Movie 3
               ├── Video4.mkv
               └── Subfolder

- **--threshold** (optional): Percentage threshold for considering partial matches (default: 95%). The program checks if the first or last 95% of the video file matches with another file. You can specify a value between 0 and 100.

## Example Usage

```
VideoDupChecker.exe "C:\path\to\folder" --mode check_folder --threshold 90
```
<br/>
For more info you can also run:

```
VideoDupChecker.exe -h  
```   

## Self-Compilation with Nuitka

If you want to compile VideoDupChecker yourself, you can do so using Nuitka. Here is the command you need to use:
```
nuitka VideoDupChecker.py --standalone --onefile --windows-icon-from-ico=icon.ico
```
