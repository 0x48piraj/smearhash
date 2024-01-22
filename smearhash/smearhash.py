"""
smearhash.smearhash
~~~~~~~~~~~~~~~~~~~
This module contains the smearhash's core functionality.
"""


import math
import os
import random
import re
import shutil
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
from PIL import Image

from .exceptions import DidNotSupplyPathOrUrl, StoragePathDoesNotExist
from .libutils import FramesExtractor, SliceNDice, Download
from .libutils import (
    create_and_return_temporary_directory,
    does_path_exists,
    get_list_of_all_files_in_dir,
)
from .libutils import video_duration, CHARSET, CHARDICT



class SmearHash:
    """
    SmearHash class provides an interface for computing the smearhash values
    for videos as well as constructing those augmented videos supported by FFmpeg.

    Pure python smearhash decoder with no additional dependencies, for both de- and encoding.
    Very close port of the original Swift BlurHash implementation by Dag Ågren.
    """

    def __init__(
        self,
        path: Optional[str] = None,
        url: Optional[str] = None,
        storage_path: Optional[str] = None,
        download_worst: bool = False,
        frame_interval: Union[int, float] = 1,
        max_components: int = 4,
        min_components: int = 2,
        work_size: int = 64,
        output_height: int = 320,
        output_width: int = 180,
    ) -> None:
        """
        :param path: Absolute path of the input video file.

        :param url: URL of the input video file. Every URL that is supported by
                    the yt-dlp package can be passed.

        :param storage_path: Storage path for the files created/downloaded by
                             the instance, pass the absolute path of the
                             directory.
                             If no argument is passed then the instance will
                             itself create the storage directory inside the
                             temporary directory of the system.

        :param download_worst: If set to True, download the worst quality video.
                               The default value is False, set True to conserve bandwidth.

        :param frame_interval: Number of frames extracted per unit time, the
                               default value is 1 per unit time. For 1 frame
                               per 5 seconds pass 1/5 or 0.2. For 5 fps pass 5.
                               Smaller frame_interval implies fewer frames and
                               vice-versa.


        :return: None

        :rtype: NoneType
        """
        self.path = path
        self.url = url

        self.storage_path = ""
        if storage_path:
            self.storage_path = storage_path

        self._storage_path = self.storage_path
        self.download_worst = download_worst
        self.frame_interval = frame_interval
        self.max_components = max_components
        self.min_components = min_components
        self.work_size = work_size
        self.output_height = output_height
        self.output_width = output_width

        # set the final intended output size
        self.output_size = (output_height, output_width)

        self.task_uid = SmearHash._get_task_uid()

        self._create_required_dirs_and_check_for_errors()

        self._copy_video_to_video_dir()

        FramesExtractor(self.video_path, self.frames_dir, interval=self.frame_interval)
        self.image_list = get_list_of_all_files_in_dir(self.frames_dir)

        self.hvconcat_path = os.path.join(self.hvconcat_dir, "hvconcat.jpg")

        self.hconcat_path = os.path.join(
            self.hconcat_dir,
            "hconcat.png",
        )

        SliceNDice(
            get_list_of_all_files_in_dir(self.frames_dir),
            self.hvconcat_path,
            self.hconcat_path,
            hvconcat_image_width=1024,
        )

        self.video_duration = video_duration(self.video_path)

        self.generate()

    def __str__(self) -> str:
        """
        The smearhash values of the instance. The hash value is 20-30 characters
        long string, indicating base83 in single-byte characters.

        :return: The string representation of the instance. The hash values of the
                 video itself form a list of hashes.

        :rtype: str
        """

        return self.hashes

    def __repr__(self) -> str:
        """
        Developer's representation of the SmearHash object.

        :return: Developer's representation of the instance.

        :rtype: str
        """

        return (
            f"SmearHash(hash={self.hashes}"
        )

    def __len__(self) -> int:
        """
        Total number of hash value strings. Total length is the number of frames defined.

        :return: Total number of hash value strings.

        :rtype: int
        """
        return len(self.hashes)

    def _copy_video_to_video_dir(self) -> None:
        """
        Copy the video from the path to the video directory.

        Copying avoids issues such as the user or some other
        process deleting the instance files while we are still
        processing.

        If instead of the path the uploader specified an url,
        then download the video and copy the file to video
        directory.


        :return: None

        :rtype: NoneType

        :raises ValueError: If the path supplied by the end user
                            lacks an extension. E.g. webm, mkv and mp4.
        """
        self.video_path: str = ""

        if self.path:
            # create a copy of the video at self.storage_path
            match = re.search(r"\.([^.]+$)", self.path)

            if match:
                extension = match.group(1)

            else:
                raise ValueError("File name (path) does not have an extension.")

            self.video_path = os.path.join(self.video_dir, (f"video.{extension}"))

            shutil.copyfile(self.path, self.video_path)

        if self.url:

            Download(
                self.url,
                self.video_download_dir,
                worst=self.download_worst,
            )

            downloaded_file = get_list_of_all_files_in_dir(self.video_download_dir)[0]
            match = re.search(r"\.(.*?)$", downloaded_file)

            extension = "mkv"

            if match:
                extension = match.group(1)

            self.video_path = f"{self.video_dir}video.{extension}"

            shutil.copyfile(downloaded_file, self.video_path)

    def _create_required_dirs_and_check_for_errors(self) -> None:
        """
        Creates important directories before the main processing starts.

        The instance files are stored in these directories, no need to worry
        about the end user or some other processes interfering with the instance
        generated files.


        :raises DidNotSupplyPathOrUrl: If the user forgot to specify both the
                                       path and the url. One of them must be
                                       specified for creating the object.

        :raises ValueError: If user passed both path and url. Only pass
                            one of them if the file is available on both
                            then pass the path only.

        :raises StoragePathDoesNotExist: If the storage path specified by the
                                         user does not exist.

        :return: None

        :rtype: NoneType
        """
        if not self.path and not self.url:
            raise DidNotSupplyPathOrUrl(
                "You must specify either a path or an URL of the video."
            )

        if self.path and self.url:
            raise ValueError("Specify either a path or an URL and NOT both.")

        if not self.storage_path:
            self.storage_path = create_and_return_temporary_directory()
        if not does_path_exists(self.storage_path):
            raise StoragePathDoesNotExist(
                f"Storage path '{self.storage_path}' does not exist."
            )

        os_path_sep = os.path.sep

        self.storage_path = os.path.join(
            self.storage_path, (f"{self.task_uid}{os_path_sep}")
        )

        self.video_dir = os.path.join(self.storage_path, (f"video{os_path_sep}"))
        Path(self.video_dir).mkdir(parents=True, exist_ok=True)

        self.video_download_dir = os.path.join(
            self.storage_path, (f"downloadedvideo{os_path_sep}")
        )
        Path(self.video_download_dir).mkdir(parents=True, exist_ok=True)

        self.frames_dir = os.path.join(self.storage_path, (f"frames{os_path_sep}"))
        Path(self.frames_dir).mkdir(parents=True, exist_ok=True)

        self.tiles_dir = os.path.join(self.storage_path, (f"tiles{os_path_sep}"))
        Path(self.tiles_dir).mkdir(parents=True, exist_ok=True)

        self.hvconcat_dir = os.path.join(self.storage_path, (f"hvconcat{os_path_sep}"))
        Path(self.hvconcat_dir).mkdir(parents=True, exist_ok=True)

        self.hconcat_dir = os.path.join(
            self.storage_path, (f"hconcat{os_path_sep}")
        )
        Path(self.hconcat_dir).mkdir(
            parents=True, exist_ok=True
        )

    def delete_storage_path(self) -> None:
        """
        Delete the storage_path directory tree.

        Remember that deleting the storage directory will also delete the
        hvconcat, extracted frames, and the downloaded video. If you passed an
        argument to the storage_path that directory will not be deleted but
        only the files and directories created inside that directory by the
        instance will be deleted, this is a feature, not a bug to ensure that
        multiple instances of the same program are not deleting the storage
        path while other instances still require that storage directory.

        Many OS delete the temporary directory on boot or they never delete it.
        If you will be calculating smearhash-value for many videos and don't
        want to run out of storage don't forget to delete the storage path.

        :return: None

        :rtype: NoneType
        """
        directory = self.storage_path

        if not self._storage_path:
            directory = (
                os.path.dirname(os.path.dirname(os.path.dirname(self.storage_path)))
                + os.path.sep
            )

        shutil.rmtree(directory, ignore_errors=True, onerror=None)

    @staticmethod
    def _get_task_uid() -> str:
        """
        Returns an unique task id for the instance. Task id is used to
        differentiate the instance files from the other unrelated files.

        We want to make sure that only the instance is manipulating the instance files
        and no other process nor user by accident deletes or edits instance files while
        we are still processing.

        :return: instance's unique task id.

        :rtype: str
        """
        sys_random = random.SystemRandom()

        return "".join(
            sys_random.choice(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            )
            for _ in range(20)
        )

    def base83_decode(self, base83_str):
        """
        Decodes a base83 string, as used in smearhash, to an integer.
        """
        value = 0
        for base83_char in base83_str:
            value = value * 83 + CHARDICT[base83_char]
        return value

    def base83_encode(self, value, length):
        """
        Decodes an integer to a base83 string, as used in smearhash.
        
        Length is how long the resulting string should be. Will complain
        if the specified length is too short.
        """
        if int(value) // (83 ** (length)) != 0:
            raise ValueError("Specified length is too short to encode given value.")

        result = ""
        for i in range(1, length + 1):
            digit = int(value) // (83 ** (length - i)) % 83
            result += CHARSET[int(digit)]
        return result

    def srgb_to_linear(self, value):
        """
        srgb 0-255 integer to linear 0.0-1.0 floating point conversion.
        """
        value = float(value) / 255.0
        if value <= 0.04045:
            return value / 12.92
        return math.pow((value + 0.055) / 1.055, 2.4)

    def sign_pow(self, value, exp):
        """
        Sign-preserving exponentiation.
        """
        return math.copysign(math.pow(abs(value), exp), value)

    def linear_to_srgb(self, value):
        """
        linear 0.0-1.0 floating point to srgb 0-255 integer conversion.
        """
        value = max(0.0, min(1.0, value))
        if value <= 0.0031308:
            return int(value * 12.92 * 255 + 0.5)
        return int((1.055 * math.pow(value, 1 / 2.4) - 0.055) * 255 + 0.5)

    def smearhash_components(self, smearhash):
        """
        Decodes and returns the number of x and y components in the given smearhash.
        """
        if len(smearhash) < 6:
            raise ValueError("smearhash must be at least 6 characters long.")

        # decode metadata
        size_info = self.base83_decode(smearhash[0])
        size_y = int(size_info / 9) + 1
        size_x = (size_info % 9) + 1

        return size_x, size_y

    def smearhash_decode(self, smearhash, width, height, punch = 1.0, linear = False):
        """
        Decodes the given smearhash to an image of the specified size.
        
        Returns the resulting image a list of lists of 3-value sRGB 8 bit integer
        lists. Set linear to True if you would prefer to get linear floating point 
        RGB back.
        
        The punch parameter can be used to de- or increase the contrast of the
        resulting image.
        
        As per the original implementation it is suggested to only decode
        to a relatively small size and then scale the result up, as it
        basically looks the same anyways.
        """
        if len(smearhash) < 6:
            raise ValueError("smearhash must be at least 6 characters long.")
        
        # decode metadata
        size_info = self.base83_decode(smearhash[0])
        size_y = int(size_info / 9) + 1
        size_x = (size_info % 9) + 1
        
        quant_max_value = self.base83_decode(smearhash[1])
        real_max_value = (float(quant_max_value + 1) / 166.0) * punch
        
        # make sure we at least have the right number of characters
        if len(smearhash) != 4 + 2 * size_x * size_y:
            raise ValueError("Invalid smearhash length.")
            
        # decode DC component
        dc_value = self.base83_decode(smearhash[2:6])
        colours = [(
            self.srgb_to_linear(dc_value >> 16),
            self.srgb_to_linear((dc_value >> 8) & 255),
            self.srgb_to_linear(dc_value & 255)
        )]
        
        # decode AC components
        for component in range(1, size_x * size_y):
            ac_value = self.base83_decode(smearhash[4+component*2:4+(component+1)*2])
            colours.append((
                self.sign_pow((float(int(ac_value / (19 * 19))) - 9.0) / 9.0, 2.0) * real_max_value,
                self.sign_pow((float(int(ac_value / 19) % 19) - 9.0) / 9.0, 2.0) * real_max_value,
                self.sign_pow((float(ac_value % 19) - 9.0) / 9.0, 2.0) * real_max_value
            ))
        
        # return image RGB values, as a list of lists of lists, 
        # consumable by something like numpy or PIL.
        pixels = []
        for y in range(height):
            pixel_row = []
            for x in range(width):
                pixel = [0.0, 0.0, 0.0]

                for j in range(size_y):
                    for i in range(size_x):
                        basis = math.cos(math.pi * float(x) * float(i) / float(width)) * \
                                math.cos(math.pi * float(y) * float(j) / float(height))
                        colour = colours[i + j * size_x]
                        pixel[0] += colour[0] * basis
                        pixel[1] += colour[1] * basis
                        pixel[2] += colour[2] * basis
                if linear == False:
                    pixel_row.append([
                        self.linear_to_srgb(pixel[0]),
                        self.linear_to_srgb(pixel[1]),
                        self.linear_to_srgb(pixel[2]),
                    ])
                else:
                    pixel_row.append(pixel)
            pixels.append(pixel_row)
        return pixels


    def smearhash_encode(self, image, components_x = 4, components_y = 4, linear = False):
        """
        Calculates the smearhash for an image using the given x and y component counts.
        
        Image should be a 3-dimensional array, with the first dimension being y, the second
        being x, and the third being the three rgb components that are assumed to be 0-255 
        srgb integers (incidentally, this is the format you will get from a PIL RGB image).
        
        You can also pass in already linear data - to do this, set linear to True. This is
        useful if you want to encode a version of your image resized to a smaller size (which
        you should ideally do in linear colour).
        """
        if components_x < 1 or components_x > 9 or components_y < 1 or components_y > 9: 
            raise ValueError("x and y component counts must be between 1 and 9 inclusive.")
        height = float(len(image))
        width = float(len(image[0]))

        # convert to linear if neeeded
        image_linear = []
        if linear == False:
            for y in range(int(height)):
                image_linear_line = []
                for x in range(int(width)):
                    image_linear_line.append([
                        self.srgb_to_linear(image[y][x][0]),
                        self.srgb_to_linear(image[y][x][1]),
                        self.srgb_to_linear(image[y][x][2])
                    ])
                image_linear.append(image_linear_line)
        else:
            image_linear = image

        # calculate components
        components = []
        max_ac_component = 0.0
        for j in range(components_y):
            for i in range(components_x):
                norm_factor = 1.0 if (i == 0 and j == 0) else 2.0
                component = [0.0, 0.0, 0.0]
                for y in range(int(height)):
                    for x in range(int(width)):
                        basis = norm_factor * math.cos(math.pi * float(i) * float(x) / width) * \
                                            math.cos(math.pi * float(j) * float(y) / height)
                        component[0] += basis * image_linear[y][x][0]
                        component[1] += basis * image_linear[y][x][1]
                        component[2] += basis * image_linear[y][x][2]

                component[0] /= (width * height)
                component[1] /= (width * height)
                component[2] /= (width * height)
                components.append(component)

                if not (i == 0 and j == 0):
                    max_ac_component = max(max_ac_component, abs(component[0]), abs(component[1]), abs(component[2]))

        # encode components
        dc_value = (self.linear_to_srgb(components[0][0]) << 16) + \
                (self.linear_to_srgb(components[0][1]) << 8) + \
                self.linear_to_srgb(components[0][2])

        quant_max_ac_component = int(max(0, min(82, math.floor(max_ac_component * 166 - 0.5))))
        ac_component_norm_factor = float(quant_max_ac_component + 1) / 166.0

        ac_values = []
        for r, g, b in components[1:]:
            ac_values.append(
                int(max(0.0, min(18.0, math.floor(self.sign_pow(r / ac_component_norm_factor, 0.5) * 9.0 + 9.5)))) * 19 * 19 + \
                int(max(0.0, min(18.0, math.floor(self.sign_pow(g / ac_component_norm_factor, 0.5) * 9.0 + 9.5)))) * 19 + \
                int(max(0.0, min(18.0, math.floor(self.sign_pow(b / ac_component_norm_factor, 0.5) * 9.0 + 9.5))))
            )

        # build final smearhash
        smearhash = ""
        smearhash += self.base83_encode((components_x - 1) + (components_y - 1) * 9, 1)
        smearhash += self.base83_encode(quant_max_ac_component, 1)
        smearhash += self.base83_encode(dc_value, 4)
        for ac_value in ac_values:
            smearhash += self.base83_encode(ac_value, 2)

        return smearhash

    def construct(self) -> None:
        for idx, hash in enumerate(self.hashes):
            # figure out what size to decode to
            decode_components_x, decode_components_y = self.smearhash_components(hash)
            decode_size_x = decode_components_x * (self.work_size // self.max_components)
            decode_size_y = decode_components_y * (self.work_size // self.max_components)
            print("Decoder working at size {} x {}".format(decode_size_x, decode_size_y))

            # decode
            decoded_image = np.array(self.smearhash_decode(hash, decode_size_x, decode_size_y, linear = True))

            # scale so that we have the right size to fill self.output_size without letter/pillarboxing
            # while matching original images aspect ratio.
            fill_x_size_y = self.output_size[0] * (self.image_size[0] / self.image_size[1])
            fill_y_size_x = self.output_size[1] * (self.image_size[1] / self.image_size[0])
            scale_target_size = list(self.output_size)
            if fill_x_size_y / self.output_size[1] < fill_y_size_x / self.output_size[0]:
                scale_target_size[0] = max(scale_target_size[0], int(fill_y_size_x))
            else:
                scale_target_size[1] = max(scale_target_size[1], int(fill_x_size_y))

            # scale (ideally, your UI layer should take care of this in some kind of efficient way)
            print("Scaling to target size: {} x {}".format(scale_target_size[0], scale_target_size[1]))
            decoded_image_large = []
            for i in range(3):
                channel_linear = Image.fromarray(decoded_image[:,:,i].astype("float32"), mode = 'F')
                decoded_image_large.append(np.array(channel_linear.resize(scale_target_size, Image.BILINEAR)))
            decoded_image_large = np.transpose(np.array(decoded_image_large), (1, 2, 0))

            # convert to srgb PIL image
            decoded_image_out = np.vectorize(self.linear_to_srgb)(np.array(decoded_image_large))
            decoded_image_out = Image.fromarray(np.array(decoded_image_out).astype('uint8'))

            # crop to final size and write
            decoded_image_out = decoded_image_out.crop((
                (decoded_image_out.width - self.output_size[0]) / 2,
                (decoded_image_out.height - self.output_size[1]) / 2,
                (decoded_image_out.width + self.output_size[0]) / 2,
                (decoded_image_out.height + self.output_size[1]) / 2,
            ))
            output_filename = f"out-{idx}.png"
            decoded_image_out.save(output_filename)
            print("Wrote final result to " + str(output_filename))


    def generate(self) -> None:
        """
        Calculates the smearhash value by utilizing the encode (base83 hash) method from
        blurhash-python package (as of now).

        :return: None

        :rtype: NoneType
        """
        smearhash_list = []
        # load the frame images and store sizes (useful for decoding later, and likely part of your metadata objects anyways)
        for filename in self.image_list:
            image = Image.open(filename).convert("RGB")
            self.image_size = (image.width, image.height)
            print("Read image " + filename + "({} x {})".format(self.image_size[0], self.image_size[1]))

            # convert to linear and thumbnail
            image_linear = np.vectorize(self.srgb_to_linear)(np.array(image))
            image_linear_thumb = []
            for i in range(3):
                channel_linear = Image.fromarray(image_linear[:,:,i].astype("float32"), mode = 'F')
                channel_linear.thumbnail((self.work_size, self.work_size))
                image_linear_thumb.append(np.array(channel_linear))
            image_linear_thumb = np.transpose(np.array(image_linear_thumb), (1, 2, 0))
            print("Encoder working at size: {} x {}".format(image_linear_thumb.shape[1], image_linear_thumb.shape[0]))

            # figure out a good component count
            components_x = int(max(self.min_components, min(self.max_components, round(image_linear_thumb.shape[1] / (self.work_size / self.max_components)))))
            components_y = int(max(self.min_components, min(self.max_components, round(image_linear_thumb.shape[0] / (self.work_size / self.max_components)))))
            print("Using component counts: {} x {}".format(components_x, components_y))

            # create smearhash
            smear_hash = self.smearhash_encode(image_linear_thumb, components_x, components_y, linear = True)

            smearhash_list.append(smear_hash)
            print("SmearHash of individual frame: " + smear_hash)

        self.hashes = smearhash_list
