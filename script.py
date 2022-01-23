#!/usr/bin/env python
import argparse
import errno
from math import floor
import ffmpeg
import sys


WAVES_BACKGROUND_IMAGE_RATIO = 0.2
WAVES_IMAGE_RATIO = 0.15


def main():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=True)
  parser.add_argument("--audio",
                      help="input audio filename", required=True)
  parser.add_argument("--background",
                      help="visualization background filename", required=True)
  parser.add_argument("--output",
                      help="output video filename", required=True)
  parser.add_argument("--vis-color", nargs='*',
                      help="colors for visualization waveforms", required=False, default=["0xffffff"])
  parser.add_argument("--background-color",
                      help="backgroundcolor for visualization waveforms", required=False, default="0x000000")

  args, _ = parser.parse_known_args()

  duration = get_audio_duration(args.audio)
  (bg_height, bg_width) = get_image_resolution(args.background)
  waves_height = floor(bg_height * WAVES_IMAGE_RATIO)
  waves_background_height = floor(bg_height * WAVES_IMAGE_RATIO)

  # Compile the waves and a background color
  stream = ffmpeg.input(args.audio)
  vis_colors = "|".join(args.vis_color)
  vid_stream = (
    stream
      .filter("showwaves", s="%dx%d" % (bg_width, waves_height), mode="cline", colors=vis_colors)
      .filter("format", "rgba")
      .filter("colorchannelmixer", aa=0.9)
  )
  background_stream = (
    ffmpeg.input("color=c=%s:s=%dx%d:d=%ss" % (args.background_color, bg_width, waves_background_height, duration), f="lavfi")
      .filter("format", "rgba")
      .filter("colorchannelmixer", aa=0.5)
  )
  waves_center_offset = floor((waves_background_height - waves_height)/2)
  viz = ffmpeg.filter([background_stream, vid_stream], 'overlay', 0, waves_center_offset)
  waves_background_center_offset = floor((bg_height - waves_background_height)/2)

  # Overlay the waves stream on top of our static image
  vid_stream = ffmpeg.filter([ffmpeg.input(args.background), viz], 'overlay', 0, waves_background_center_offset)
  ffmpeg.output(stream.audio, vid_stream, args.output).run()


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