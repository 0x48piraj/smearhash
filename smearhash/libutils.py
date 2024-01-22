"""
smearhash.libutils
~~~~~~~~~~~~~~~~~~~
This module contains the smearhash's utilities and shared classes.
"""


import os
import re
import tempfile
import shlex
from shutil import which
from math import ceil, sqrt
from pathlib import Path
from PIL import Image
from subprocess import PIPE, Popen, check_output
from typing import Optional, Union, List

from .exceptions import (
    FFmpegError,
    FFmpegFailedToExtractFrames,
    FFmpegNotFound,
    FramesExtractorOutPutDirDoesNotExist,
    GridOfZeroFramesError,
    DownloadFailed,
    DownloadOutPutDirDoesNotExist
)



# characters for base83
CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%*+,-.:;=?@[]^_{|}~"
CHARDICT = dict(zip(CHARSET, range(len(CHARSET))))


def get_list_of_all_files_in_dir(directory: str) -> List[str]:
    """
    Returns a list containing all the file paths(absolute path) in a directory.
    The list is sorted.

    :return: List of absolute path of all files in a directory.

    :rtype: List[str]
    """
    return sorted([(directory + filename) for filename in os.listdir(directory)])


def does_path_exists(path: str) -> bool:
    """
    If a directory is supplied then check if it exists.
    If a file is supplied then check if it exists.

    Directory ends with "/" on posix or "\" in windows and files do not.

    If directory/file exists returns True else returns False

    :return: True if dir or file exists else False.

    :rtype: bool
    """
    if path.endswith("/") or path.endswith("\\"):
        # it's directory
        return os.path.isdir(path)

    else:
        # it's file
        return os.path.isfile(path)


def create_and_return_temporary_directory() -> str:
    """
    create a temporary directory where we can store the video, frames and the
    hvconcat.

    :return: Absolute path of the empty directory.

    :rtype: str
    """
    path = os.path.join(tempfile.mkdtemp(), ("temp_storage_dir" + os.path.sep))
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def video_duration(video_path: str, ffmpeg_path: Optional[str] = None) -> float:
    """
    Retrieve the exact video duration as echoed by the FFmpeg and return
    the duration in seconds. Maximum duration supported is 999 hours, above
    which the regex is doomed to fail(no match).

    :param video_path: Absolute path of the video file.

    :param ffmpeg_path: Path of the FFmpeg software if not in path.

    :return: Video length(duration) in seconds.

    :rtype: float
    """

    if not ffmpeg_path:
        ffmpeg_path = str(which("ffmpeg"))

    command = f'"{ffmpeg_path}" -i "{video_path}"'
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    output, error = process.communicate()

    match = re.search(
        r"Duration\:(\s\d?\d\d\:\d\d\:\d\d\.\d\d)\,",
        (output.decode() + error.decode()),
    )

    if match:
        duration_string = match.group(1)

    hours, minutes, seconds = duration_string.strip().split(":")

    return float(hours) * 60.00 * 60.00 + float(minutes) * 60.00 + float(seconds)


class FramesExtractor:

    """
    Extract frames from the input video file and save at the output directory(frame storage directory).
    """

    def __init__(
        self,
        video_path: str,
        output_dir: str,
        interval: Union[int, float] = 1,
        ffmpeg_path: Optional[str] = None,
    ) -> None:
        """
        Raises Exeception if video_path does not exists.
        Raises Exeception if output_dir does not exists or if not a directory.

        Checks  the ffmpeg installation and the path; thus ensure that we can use it.

        :return: None

        :rtype: NoneType

        :param video_path: absolute path of the video

        :param output_dir: absolute path of the directory
                           where to save the frames.

        :param interval: interval is seconds. interval must be an integer.
                         Extract one frame every given number of seconds.
                         Default is 1, that is one frame every second.

        :param ffmpeg_path: path of the ffmpeg software if not in path.

        """
        self.video_path = video_path
        self.output_dir = output_dir
        self.interval = interval
        self.ffmpeg_path = ""
        if ffmpeg_path:
            self.ffmpeg_path = ffmpeg_path

        if not does_path_exists(self.video_path):
            raise FileNotFoundError(
                f"No video found at '{self.video_path}' for frame extraction."
            )

        if not does_path_exists(self.output_dir):
            raise FramesExtractorOutPutDirDoesNotExist(
                f"No directory called '{self.output_dir}' found for storing the frames."
            )

        self._check_ffmpeg()

        self.extract()

    def _check_ffmpeg(self) -> None:
        """
        Checks the ffmpeg path and runs 'ffmpeg -version' to verify that the
        software, ffmpeg is found and works.

        :return: None

        :rtype: NoneType
        """

        if not self.ffmpeg_path:

            if not which("ffmpeg"):

                raise FFmpegNotFound(
                    "FFmpeg is not on the system path. Install FFmpeg and add it to the path."
                    + "Or you can also pass the path via the 'ffmpeg_path' parameter."
                )
            else:

                self.ffmpeg_path = str(which("ffmpeg"))

        # Check the ffmpeg
        try:
            # check_output will raise FileNotFoundError if it does not finds the ffmpeg
            output = check_output([str(self.ffmpeg_path), "-version"]).decode()

        except FileNotFoundError:
            raise FFmpegNotFound(f"FFmpeg not found at '{self.ffmpeg_path}'.")

        else:

            if "ffmpeg version" not in output:
                raise FFmpegError(
                    f"ffmpeg at '{self.ffmpeg_path}' is not really ffmpeg. Output of ffmpeg -version is \n'{output}'."
                )

    @staticmethod
    def detect_crop(
        video_path: Optional[str] = None,
        frames: int = 3,
        ffmpeg_path: Optional[str] = None,
    ) -> str:
        """
        Detects the amount of cropping to remove black bars.

        The method uses [ffmpeg.git] / libavfilter /vf_cropdetect.c
        to detect_crop for some fixed intervals.

        The mode of the detected crops is selected as the crop required.

        :return: FFmpeg argument -vf filter and confromable crop parameter.

        :rtype: str
        """

        # we look upto the 120th minute into the video to detect the most
        # precise crop value
        time_start_list = [
            2,
            5,
            10,
            20,
            40,
            100,
            300,
            600,
            1200,
            2400,
            7200,
            14400,
        ]

        crop_list = []

        for start_time in time_start_list:

            command = f'"{ffmpeg_path}" -ss {start_time} -i "{video_path}" -vframes {frames} -vf cropdetect -f null -'

            process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)

            output, error = process.communicate()

            matches = re.findall(
                r"crop\=[0-9]{1,4}:[0-9]{1,4}:[0-9]{1,4}:[0-9]{1,4}",
                (output.decode() + error.decode()),
            )

            for match in matches:
                crop_list.append(match)

        mode = None
        if len(crop_list) > 0:
            mode = max(crop_list, key=crop_list.count)

        crop = " "
        if mode:
            crop = f" -vf {mode} "

        return crop

    def extract(self) -> None:
        """
        Extract the frames at every n seconds where n is the
        integer set to self.interval.

        :return: None

        :rtype: NoneType
        """

        ffmpeg_path = self.ffmpeg_path
        video_path = self.video_path
        output_dir = self.output_dir

        if os.name == "posix":
            ffmpeg_path = shlex.quote(self.ffmpeg_path)
            video_path = shlex.quote(self.video_path)
            output_dir = shlex.quote(self.output_dir)

        crop = FramesExtractor.detect_crop(
            video_path=video_path, frames=3, ffmpeg_path=ffmpeg_path
        )

        command = (
            f'"{ffmpeg_path}"'
            + " -i "
            + f'"{video_path}"'
            + f"{crop}"
            + " -s 144x144 "
            + " -r "
            + str(self.interval)
            + " "
            + '"'
            + output_dir
            + "video_frame_%07d.jpeg"
            + '"'
        )

        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = process.communicate()

        ffmpeg_output = output.decode()
        ffmpeg_error = error.decode()

        if len(os.listdir(self.output_dir)) == 0:

            raise FFmpegFailedToExtractFrames(
                f"FFmpeg could not extract any frames.\n{command}\n{ffmpeg_output}\n{ffmpeg_error}"
            )


class SliceNDice:

    """
    Class that creates hv/h concatenated versions from list of images.

    hvconcat that should be as close to the shape of a square.

    The images are arranged by timestamp of the frames, their
    index in the image_list is based on thier timestamp on the
    video. The image with the index 2 is a frame from the 3rd
    second and an index 39 is from at the 40th second. The index
    is one less due to zero-based indexing.


    Let's say we have a list with 9 images.

    As the images should be arranged in a way to resemble a
    square, we take the square root of 9 and that is 3. Now
    we need to make a 3x3 frames hvconcat.

    Arrangement should be:
    Img1 Img2 Img3
    Img4 Img5 Img6
    Img7 Img8 Img9

    If the number of images is not a perfect square, calculate the
    square root and round it to the nearest integer.

    If number of images is 13, which is not a perfect square.

    sqrt(13) = 3.605551275463989
    round(3.605551275463989) = 4

    Thus the image should be 4x4 frames of hvconcat.

    Arrangement should be:
    -----------------------------
    |  Img1  Img2  Img3   Img4  |
    |  Img5  Img6  Img7   Img8  |
    |  Img9  Img10 Img11  Img12 |
    |  Img13  X     X      X    |
    -----------------------------

    X denotes the empty space due to lack of images.
    But the empty spaces will not affect the robustness
    as downsized/transcoded version of the video will also
    produce these vacant spaces.
    """

    def __init__(
        self,
        image_list: List[str],
        hvconcat_output_path: str,
        hconcat_output_path: str,
        hvconcat_image_width: int = 1024,
    ) -> None:
        """
        Checks if the list passed is not an empty list.
        Also makes sure that the hvconcat_output_path directory exists.

        And calls the make method, the make method creates the hvconcat.

        :param image_list: A python list containing the list of absolute
                           path of images that are to be added in the hvconcat.
                           The order of images is kept intact and is very important.

        :param hvconcat_output_path: Absolute path of the hvconcat including
                            the image name. (This is where the hvconcat is saved.)
                            Example: '/home/username/projects/hvconcat.jpeg'.

        :param hvconcat_image_width: An integer specifying the image width of the
                                    output hvconcat. Default value is 1024 pixels.

        :return: None

        :rtype: NoneType
        """
        self.image_list = image_list
        self.number_of_images = len(self.image_list)
        self.hvconcat_output_path = hvconcat_output_path
        self.hconcat_output_path = hconcat_output_path
        self.hvconcat_image_width = hvconcat_image_width

        self.images_per_row_in_hvconcat = int(round(sqrt(self.number_of_images)))

        if self.number_of_images == 0:
            raise GridOfZeroFramesError("Can not make a hvconcat of zero images.")

        hvconcat_output_path_dir = os.path.dirname(self.hvconcat_output_path) + "/"
        if not does_path_exists(hvconcat_output_path_dir):
            raise FileNotFoundError(
                "Directory at which output hvconcat is to be saved does not exists."
            )
        hconcat_output_path_dir = os.path.dirname(self.hconcat_output_path) + "/"
        if not does_path_exists(hconcat_output_path_dir):
            raise FileNotFoundError(
                "Directory at which output hconcat is to be saved does not exists."
            )

        self.concatenate_video_frames_grid()
        self.concatenate_video_frames_horizontally()

    def concatenate_video_frames_grid(self) -> None:
        """
        Creates the hvconcat from the list of images.

        It calculates the scale of the images on hvconcat by
        measuring the first image width and height, there's no
        reason for choosing first one and it's arbitrary. But
        we assume that all the images passed should have same size.

        A base image of 'hvconcat_image_width' width and of 'number
        of rows times scaled frame image height' height is created.
        The base image has all pixels with RGB value 0,0,0 that is
        the base image is pure black. The frame images are now embeded
        on it.
        The frame images are scaled to fit the hvconcat base image such
        that the shape of hvconcat is as close to the shape of a square.

        :return: None

        :rtype: NoneType
        """

        # arbitrarily selecting the first image from the list, index 0
        with Image.open(self.image_list[0]) as first_frame_image_in_list:

            # find the width and height of the first image of the list.
            # Assuming all the images have same size.
            frame_image_width, frame_image_height = first_frame_image_in_list.size

        # scale is the ratio of hvconcat_image_width and product of
        # images_per_row_in_hvconcat with frame_image_width.

        # the scale will always lie between 0 and 1, which implies that
        # the images are always going to get downsized.
        scale = (self.hvconcat_image_width) / (
            self.images_per_row_in_hvconcat * frame_image_width
        )

        # calculating the scaled height and width for the frame image.
        scaled_frame_image_width = ceil(frame_image_width * scale)
        scaled_frame_image_height = ceil(frame_image_height * scale)

        # divide the number of images by images_per_row_in_hvconcat. The later
        # was calculated by taking the square root of total number of images.
        number_of_rows = ceil(self.number_of_images / self.images_per_row_in_hvconcat)

        # multiplying the height of one downsized image with number of rows.
        # height of 1 downsized image is product of scale and frame_image_height
        # total height is number of rows times the height of one downsized image.
        self.hvconcat_image_height = ceil(scale * frame_image_height * number_of_rows)

        # create an image of passed hvconcat_image_width and calculated hvconcat_image_height.
        # the downsized images will be pasted on this new base image.
        # the image is 0,0,0 RGB(black).
        hvconcat_image = Image.new(
            "RGB", (self.hvconcat_image_width, self.hvconcat_image_height)
        )

        # keep track of the x and y coordinates of the resized frame images
        i, j = (0, 0)

        # iterate the frames and paste them on their position on the hvconcat_image
        for count, frame_path in enumerate(self.image_list):

            # set the x coordinate to zero if we are on the first column
            # if self.images_per_row_in_hvconcat is 4
            # then 0,4,8 and so on should have their x coordinate as 0
            if (count % self.images_per_row_in_hvconcat) == 0:
                i = 0

            # open the frame image, must open it to resize it using the thumbnail method
            frame = Image.open(frame_path)

            # scale the opened frame images
            frame.thumbnail(
                (scaled_frame_image_width, scaled_frame_image_height), Image.ANTIALIAS
            )

            # set the value of x to that of i's value.
            # i is set to 0 if we are on the first column.
            x = i

            # it ensures that y coordinate stays the same for any given row.
            # the floor of a real number is the largest integer that is less
            # than or equal to the number. floor division is used because of
            # the zero based indexing, the floor of the division stays same
            # for an entier row as the decimal values are negled by the floor.
            # for the first row the result of floor division is always zero and
            # the product of 0 with scaled_frame_image_height is also zero, they
            # y coordinate for the first row is 0.
            # for the second row the result of floor division is one and the prodcut
            # with scaled_frame_image_height ensures that the y coordinate is
            # scaled_frame_image_height below the first row.
            y = (j // self.images_per_row_in_hvconcat) * scaled_frame_image_height

            # paste the frame image on the newly created base image(base image is black)
            hvconcat_image.paste(frame, (x, y))
            frame.close()

            # increase the x coordinate by scaled_frame_image_width
            # to get the x coordinate of the next frame. unless the next image
            # will be on the very first column this will be the x coordinate.
            i = i + scaled_frame_image_width

            # increase the value of j by 1, this is to calculate the y coordinate of
            # next image. The increased number will be floor divided by images_per_row_in_hvconcat
            # therefore the y coordinate stays the same for any given row.
            j += 1

        # save the base image with all the scaled frame images embeded on it.
        hvconcat_image.save(self.hvconcat_output_path)
        hvconcat_image.close()

    def concatenate_video_frames_horizontally(self) -> None:
        image_file_names = self.image_list
        total_images = len(image_file_names)
        first_image_filename = image_file_names[0]
        with Image.open(first_image_filename) as first_frame_image_in_list:
            width, height = first_frame_image_in_list.size

        base_image = Image.new("RGB", (width * total_images, height))

        x_offset = 0
        for image_filename in image_file_names:
            img = Image.open(image_filename)
            base_image.paste(img, (x_offset, 0))
            img.close()
            x_offset += width

        base_image.save(self.hconcat_output_path)


class Download:

    """
    Class that downloads the video prior to frames extraction.

    Tries to download the lowest quality video possible.
    Uses yt-dlp to download the videos.
    """

    def __init__(
        self,
        url: str,
        output_dir: str,
        worst: bool = True,
    ) -> None:
        """
        :param url: The URL of the video. The video will be
                    downloaded from this url. Must be a string.

        :param output_dir: The directory where the downloaded video will be stored.
                           Must be a string and path must be absolute.

        :param worst: The quality of video downloaded by yt-dlp.
                      True for worst quality and False for the default settings
                      of the downloader. Default value for worst is True.

        :return: None

        :rtype: NoneType
        """
        self.url = url
        self.output_dir = output_dir
        self.worst = worst

        if not does_path_exists(self.output_dir):
            raise DownloadOutPutDirDoesNotExist(
                f"No directory found at '{self.output_dir}' for storing the downloaded video. Can not download the video."
            )

        self.yt_dlp_path = str(which("yt-dlp"))
        self.download_video()

    def download_video(self) -> None:
        """Download the video from URL

        :return: None

        :rtype: NoneType

        """
        worst = " "
        if self.worst:
            worst = " -f worst "

        command = (
            f'"{self.yt_dlp_path}"'
            + worst
            + " "
            + '"'
            + self.url
            + '"'
            + " -o "
            + '"'
            + self.output_dir
            + "video_file.%(ext)s"
            + '"'
        )

        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = process.communicate()
        yt_dlp_output = output.decode()
        yt_dlp_error = error.decode()

        if len(get_list_of_all_files_in_dir(self.output_dir)) == 0:
            raise DownloadFailed(
                f"'{self.yt_dlp_path}' failed to download the video at"
                + f" '{self.url}'.\n{yt_dlp_output}\n{yt_dlp_error}"
            )
