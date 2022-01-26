#!/usr/bin/env python
import argparse
import errno
from math import floor
import ffmpeg
import sys


# Arg validation for floats
def restricted_float(x):
  try:
    x = float(x)
  except ValueError:
    raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

  if x < 0.0 or x > 1.0:
    raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
  return x


def main():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=True)
  parser.add_argument("--audio",
                      help="input audio filename", required=True)
  parser.add_argument("--background",
                      help="visualization background filename", required=True)
  parser.add_argument("--output",
                      help="output video filename", required=True)
  parser.add_argument("--vis-background-to-vid-ratio", type=restricted_float, default=0.2,
                      help="ratio of visualization background height to input image height (0.0-1.0)", required=False)
  parser.add_argument("--vis-waves-to-vid-ratio", type=restricted_float, default=0.15,
                      help="ratio of visualization waves height to input image height (0.0-1.0)", required=False)
  parser.add_argument("--vis-color", nargs='*', required=False, default=["0xffffff"],
                      help="colors for visualization waveforms")
  parser.add_argument("--vis-color-opacity", type=restricted_float, default=0.9,
                      help="opacity of vis colors (0.0-1.0)", required=False)
  parser.add_argument("--background-color", required=False, default="0x000000",
                      help="background color for visualization waveforms")
  parser.add_argument("--background-color-opacity", type=restricted_float, default=0.5,
                      help="opacity for visualization background color (0.0-1.0)", required=False)

  args, _ = parser.parse_known_args()

  # Get metadata for visualization
  duration = get_audio_duration(args.audio)
  (bg_height, bg_width) = get_image_resolution(args.background)
  waves_height = floor(bg_height * args.vis_waves_to_vid_ratio)
  waves_background_height = floor(bg_height * args.vis_background_to_vid_ratio)

  # Compile the waves and a background color
  stream = ffmpeg.input(args.audio)
  vis_colors = "|".join(args.vis_color)
  vid_stream = get_audio_waveforms(stream, bg_width, waves_height, vis_colors, args.vis_color_opacity)
  background_stream = generate_background_color(bg_width, waves_background_height, args.background_color,
                                                args.background_color_opacity, duration)
  waves_center_offset = floor((waves_background_height - waves_height)/2)
  viz = ffmpeg.filter([background_stream, vid_stream], 'overlay', 0, waves_center_offset)
  waves_background_center_offset = floor((bg_height - waves_background_height)/2)

  # Overlay the waves stream on top of our static image
  vid_stream = ffmpeg.filter([ffmpeg.input(args.background), viz], 'overlay', 0, waves_background_center_offset)
  ffmpeg.output(stream.audio, vid_stream, args.output).run()


# Generate a static color background video stream
def generate_background_color(width, height, color, opacity, duration_in_seconds):
  return (
    ffmpeg.input("color=c=%s:s=%dx%d:d=%ss" % (color, width, height, duration_in_seconds), f="lavfi")
          .filter("format", "rgba")
          .filter("colorchannelmixer", aa=opacity)
  )

# Given an input AV source, generate visualization waves
def get_audio_waveforms(av_stream, width, height, colors, opacity):
  return (
    av_stream
      .filter("showwaves", s="%dx%d" % (width, height), mode="cline", colors=colors)
      .filter("format", "rgba")
      .filter("colorchannelmixer", aa=opacity)
  )

# Get image resolution using ffprobe
def get_image_resolution(image_filename):
  metadata = get_metadata(image_filename)
  height = metadata["streams"][0]["height"]
  width = metadata["streams"][0]["width"]
  return (height, width)


# Get audio duration using ffprobe
def get_audio_duration(audio_filename):
  metadata = get_metadata(audio_filename)
  return metadata["format"]["duration"]


# Get metadata about file from ffprob
def get_metadata(filename):
  metadata = ffmpeg.probe(filename)
  return metadata


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    # The user asked the program to exit
    sys.exit(1)
  except IOError as e:
    # When this program is used in a shell pipeline and an earlier program in
    # the pipeline is terminated, we'll receive an EPIPE error.  This is normal
    # and just an indication that we should exit after processing whatever
    # input we've received -- we don't consume standard input so we can just
    # exit cleanly in that case.
    if e.errno != errno.EPIPE:
      raise

    # We still exit with a non-zero exit code though in order to propagate the
    # error code of the earlier process that was terminated.
    sys.exit(1)

  sys.exit(0)