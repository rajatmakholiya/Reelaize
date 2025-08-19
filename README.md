Video Splitter
A simple desktop application for splitting large video files into smaller, equal-duration clips. This tool is built with Python's Tkinter library and uses FFmpeg for video processing. It provides options for changing the aspect ratio and adding part numbers, making it ideal for preparing videos for social media platforms.

Features
Easy-to-use Interface: A clean and straightforward graphical user interface for selecting files and options.

Custom Clip Duration: Specify the length of each smaller clip in seconds.

Aspect Ratio Conversion:

Keep the original aspect ratio.

Convert to a vertical Reels (9:16) format with a blurred background.

Convert to a Square (1:1) format, also with a blurred background.

Add Part Numbers: Automatically overlay "Part X" text on each corresponding video clip.

Efficient Processing:

Uses ffmpeg -c copy for fast, lossless splitting when no re-encoding is needed.

Applies filters and re-encodes only when changing the aspect ratio or adding text.

Real-time Logging: View the live FFmpeg output to monitor the progress and troubleshoot any issues.

Cross-Platform: Compatible with Windows, macOS, and Linux (as long as Python and FFmpeg are installed).

Requirements
Python 3.x

FFmpeg: You must have FFmpeg installed and accessible in your system's PATH. The application will check for ffmpeg and ffprobe on startup. You can download it from ffmpeg.org.

How to Use
Run the application:

Bash

python video-splitter.py

Select Video File: Click the "Browse..." button next to "Video File" to choose the video you want to split.

Select Output Folder: Click the "Browse..." button next to "Output Folder" to choose where the split clips will be saved.

Set Clip Duration: Enter the desired duration for each clip in seconds (e.g., 60).

Choose Aspect Ratio: Select the desired output aspect ratio from the dropdown menu.

(Optional) Add Part Number: Check the "Add Part Number Text" box if you want to label each clip.

Start Splitting: Click the "Start Splitting" button to begin the process.

Monitor Progress: Watch the progress bar and the FFmpeg log to see the status. You will receive a notification when the process is complete.

FFmpeg Filter Explanation
When you choose to change the aspect ratio or add subtitles, the script constructs a complex FFmpeg filter chain. Here's a breakdown of how it works for the "Reels (9:16)" option:

[0:v]split[original][copy];
[copy]scale=w=1080:h=1920:force_original_aspect_ratio=increase,crop=w=1080:h=1920,boxblur=10:5[background];
[original]scale=w=1080:h=1920:force_original_aspect_ratio=decrease[foreground];
[background][foreground]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2
[0:v]split[original][copy]: Creates two identical streams from the source video ([0:v]). One is named [original] and the other [copy].

[copy]scale=...,crop=...,boxblur=...[background]:

The [copy] stream is scaled up to fill a 1080x1920 frame (force_original_aspect_ratio=increase).

It's then cropped to a strict 1080x1920 size.

A boxblur filter is applied to create the blurred background effect.

This resulting stream is named [background].

[original]scale=...[foreground]:

The [original] stream is scaled down to fit within the 1080x1920 frame without cropping (force_original_aspect_ratio=decrease).

This becomes the [foreground] stream.

[background][foreground]overlay=...: The sharp [foreground] video is placed on top of the blurred [background] video, centered on the screen.

When the "Add Part Number" option is selected, a drawtext filter is appended to add the text overlay.
