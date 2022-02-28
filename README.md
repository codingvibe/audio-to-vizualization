# Audio to Visualization

The purpose of this small Python script is to transform an audio file in to a video using a background image and an audio visualizer. This tool was written leveraging ffmpeg and requires it be installed and accessible via the `ffmpeg` command on the command line.

## FFMPEG
Download `ffmpeg` and get access to the documentation at https://www.ffmpeg.org/

## Requirements
Install via pip:

`pip install -r requirements.txt`

## Run the script

`python audio_to_visualization.py <arguments>`

### Command line arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| --audio | path to audio file to visualize | true | N/A |
| --background | path to image to use for background | true | N/A |
| --output | path and name of output file. Must end in .mp4 | true | N/a |
| --vis-background-to-vid-ratio | ratio of visualization background height to input image height (0.0-1.0) | false | 0.2 |
| --vis-waves-to-vid-ratio | ratio of visualization waves height to input image height (0.0-1.0) | false | 0.15 |
| --vis-color | color for visualization waveforms. can be used multiple times | false | "0xffffff" |
| --vis-color-opacity | opacity of vis colors (0.0-1.0) | false | 0.9 |
| --background-color | background color for visualization waveforms | false | "0x000000" |
| --background-color-opacity | opacity for visualization background color (0.0-1.0) | false | 0.5 |
