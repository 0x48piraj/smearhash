#       ___           ___           ___           ___           ___           ___           ___           ___           ___     
#      /\  \         /\__\         /\  \         /\  \         /\  \         /\__\         /\  \         /\  \         /\__\    
#     /::\  \       /::|  |       /::\  \       /::\  \       /::\  \       /:/  /        /::\  \       /::\  \       /:/  /    
#    /:/\ \  \     /:|:|  |      /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/__/        /:/\:\  \     /:/\ \  \     /:/__/     
#   _\:\~\ \  \   /:/|:|__|__   /::\~\:\  \   /::\~\:\  \   /::\~\:\  \   /::\  \ ___   /::\~\:\  \   _\:\~\ \  \   /::\  \ ___ 
#  /\ \:\ \ \__\ /:/ |::::\__\ /:/\:\ \:\__\ /:/\:\ \:\__\ /:/\:\ \:\__\ /:/\:\  /\__\ /:/\:\ \:\__\ /\ \:\ \ \__\ /:/\:\  /\__\
#  \:\ \:\ \/__/ \/__/~~/:/  / \:\~\:\ \/__/ \/__\:\/:/  / \/_|::\/:/  / \/__\:\/:/  / \/__\:\/:/  / \:\ \:\ \/__/ \/__\:\/:/  /
#   \:\ \:\__\         /:/  /   \:\ \:\__\        \::/  /     |:|::/  /       \::/  /       \::/  /   \:\ \:\__\        \::/  / 
#    \:\/:/  /        /:/  /     \:\ \/__/        /:/  /      |:|\/__/        /:/  /        /:/  /     \:\/:/  /        /:/  /  
#     \::/  /        /:/  /       \:\__\         /:/  /       |:|  |         /:/  /        /:/  /       \::/  /        /:/  /   
#      \/__/         \/__/         \/__/         \/__/         \|__|         \/__/         \/__/         \/__/         \/__/    Piyush Raj (@0x48piraj)


"""
The Python package for SmearHash: A very compact representation of a placeholder for a video.

https://github.com/0x48piraj/smearhash

Usage:

>>> from smearhash import SmearHash
>>> # video: The Zipf Mystery by Vsauce
>>> smearhash = SmearHash(url="https://www.youtube.com/watch?v=fCn8zs912OE", download_worst=False)
>>>
>>> smearhash.hashes # smearhash values of the file
['...', '...', '...', '...']
>>>
>>> path = "/home/0x48piraj/Downloads/RickRoll.mkv"
>>> smearhash = SmearHash(path=path)
>>> smearhash.hashes
['...', '...', '...', '...']


Extended Usage : https://github.com/0x48piraj/smearhash/wiki/Extended-Usage

API Reference : https://github.com/0x48piraj/smearhash/wiki/API-Reference


:copyright: (c) 2024 Piyush Raj
:license: MIT, see LICENSE for more details.
:pypi: https://pypi.org/project/smearhash/
:wiki: https://github.com/0x48piraj/smearhash/wiki
"""

from .__version__ import (
    __author__,
    __author_email__,
    __copyright__,
    __description__,
    __license__,
    __status__,
    __title__,
    __url__,
    __version__,
)
from .exceptions import (
    GridOfZeroFramesError,
    DidNotSupplyPathOrUrl,
    DownloadFailed,
    DownloadOutPutDirDoesNotExist,
    FFmpegError,
    FFmpegFailedToExtractFrames,
    FFmpegNotFound,
    FramesExtractorOutPutDirDoesNotExist,
    StoragePathDoesNotExist,
    SmearHashError,
)
from .smearhash import SmearHash


__all__ = ['SmearHash']