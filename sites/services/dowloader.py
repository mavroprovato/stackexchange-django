"""Helper class that downloads files from the Stack Exchange Data Dump located in the Internet archive
(https://archive.org/details/stackexchange).
"""
import logging
import pathlib

import requests
import tqdm

from django.conf import settings

# The module logger
logger = logging.getLogger(__name__)


class Downloader:
    """Helper class to files from the Exchange Data Dump. Uses caching in order not to download files when they are
    already downloaded.
    """
    # The base URL
    BASE_URL = 'https://archive.org/download/stackexchange'
    # Timeout in seconds
    TIMEOUT = 60

    def __init__(self, filename: str):
        """Create the file downloader.

        :param filename: The name of the file to download.
        """
        self.filename = filename
        self._cache_dir = pathlib.Path(settings.BASE_DIR) / "var" / "cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def get_file(self) -> pathlib.Path:
        """Get the file, either by downloading it or by returning the cached version.

        :return: The file.
        """
        if self.should_download():
            self.download()
        else:
            logger.info("File %s is up to date", self.filename)

        return self._cache_dir / self.filename

    def should_download(self) -> bool:
        """Check if the file should be downloaded.

        :return: True if the file should be downloaded, false otherwise.
        """
        if not (self._cache_dir / self.filename).exists():
            logger.info("File %s does not exist in cache", self.filename)
            return True
        if self.file_changed():
            return True

        return False

    def file_changed(self) -> bool:
        """Check if the dump file has changed.

        :return: True if the dump file has changed, False otherwise.
        """
        # Get the latest file etag
        response = requests.head(f"{self.BASE_URL}/{self.filename}", allow_redirects=True, timeout=self.TIMEOUT)
        response.raise_for_status()
        remote_etag = response.headers['Etag'].strip('"')

        # Get the cached file etag
        etag_file = self._cache_dir / f"{self.filename}.etag"
        if not etag_file.exists():
            logger.info("Cache info for file %s does not exist", self.filename)
            return True

        # Check if the file has changed
        with etag_file.open('r') as f:
            local_etag = f.read()
            if remote_etag != local_etag:
                logger.info("File %s has changed from the cached version", self.filename)
                return True

        logger.info("Cache for file %s is up to date", self.filename)

        return False

    def download(self) -> None:
        """Download the dump file.
        """
        logger.info("Downloading file %s", self.filename)

        # Download file
        with requests.get(f"{self.BASE_URL}/{self.filename}", stream=True, timeout=self.TIMEOUT) as response:
            response.raise_for_status()
            total = int(response.headers.get('content-length', 0))
            with (
                (self._cache_dir / f"{self.filename}").open('wb') as f,
                tqdm.tqdm(desc=self.filename, total=total, unit='iB', unit_scale=True) as progress_bar
            ):
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    progress_bar.update(size)

        # Write the cache information
        with (self._cache_dir / f"{self.filename}.etag").open('wt') as f:
            f.write(response.headers['ETag'].strip('"'))
