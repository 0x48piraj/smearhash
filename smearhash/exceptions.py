"""
smearhash.exceptions
~~~~~~~~~~~~~~~~~~~
This module contains the smearhash's exceptions.
"""


class SmearHashError(Exception):

    """Base Exception for the smearhash package."""

    pass


class StoragePathDoesNotExist(SmearHashError):

    """
    The storage path passed by the user does not exist.
    The hvconcat is the image representing your video as an two dimensional bitmap image.
    """

    pass


class FramesExtractorOutPutDirDoesNotExist(SmearHashError):

    """The frames output directory passed to the frame extractor does not exist."""

    pass


class DownloadOutPutDirDoesNotExist(SmearHashError):

    """The output directory passed to downloader for storing the downloaded video does not exist."""

    pass


class DidNotSupplyPathOrUrl(SmearHashError):

    """Must supply either a path for the video or a valid URL"""

    pass


class GridOfZeroFramesError(SmearHashError):

    """Raised if zero frames are passed for hvconcat making."""

    pass


class DownloadFailed(SmearHashError):

    """Download software failed to download the video from the url."""

    pass


class FFmpegError(SmearHashError):

    """Base error for the FFmpeg software."""

    pass


class FFmpegNotFound(FFmpegError):

    """FFmpeg is either not installed or not in the executable path of the system."""

    pass


class FFmpegFailedToExtractFrames(FFmpegError):

    """FFmpeg failed to extract any frame at all. Maybe the input video is damaged or corrupt."""

    pass
