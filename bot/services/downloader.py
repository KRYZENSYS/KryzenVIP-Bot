"""Downloader service using yt-dlp."""
import asyncio
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from loguru import logger


class Downloader:
    def __init__(self) -> None:
        self.work_dir = Path(tempfile.mkdtemp(prefix="kryzen_dl_"))
        logger.info(f"Downloader work dir: {self.work_dir}")

    async def download(self, url: str, platform: str = "auto") -> Optional[Path]:
        try:
            return await self._run_yt_dlp(url, platform)
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    async def _run_yt_dlp(self, url: str, platform: str) -> Optional[Path]:
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--no-playlist",
            "--no-warnings",
            "--no-progress",
            "--max-filesize", "100M",
            "-o", str(self.work_dir / "%(title).50s.%(ext)s"),
            "--merge-output-format", "mp4",
            url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=180)
        except asyncio.TimeoutError:
            proc.kill()
            raise

        if proc.returncode != 0:
            err = stderr.decode(errors="ignore")[:500]
            logger.error(f"yt-dlp failed: {err}")
            raise RuntimeError(f"yt-dlp error: {err[:200]}")

        files = sorted(self.work_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        files = [f for f in files if f.is_file() and f.stat().st_size > 0]
        return files[0] if files else None

    def cleanup(self) -> None:
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir, ignore_errors=True)


downloader = Downloader()