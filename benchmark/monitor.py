from __future__ import annotations

import threading
from dataclasses import dataclass

import psutil


@dataclass
class ResourceStats:
    avg_cpu_percent: float
    peak_ram_mb: float
    avg_ram_mb: float


class SystemMonitor:
    """Samples whole-host utilization; run DBs sequentially so scope is comparable."""

    def __init__(self, interval: float = 0.01):
        self.interval = interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.cpu: list[float] = []
        self.ram: list[float] = []
        self._start_times = None

    def _sample(self) -> None:
        while not self._stop.wait(self.interval):
            self.ram.append(psutil.virtual_memory().used / (1024 * 1024))

    def __enter__(self) -> "SystemMonitor":
        self._start_times = psutil.cpu_times()
        self.ram.append(psutil.virtual_memory().used / (1024 * 1024))
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        self.ram.append(psutil.virtual_memory().used / (1024 * 1024))
        end = psutil.cpu_times()
        if self._start_times is not None:
            total = sum(end) - sum(self._start_times)
            idle = (end.idle - self._start_times.idle) + (
                getattr(end, "iowait", 0.0) - getattr(self._start_times, "iowait", 0.0)
            )
            self.cpu.append(
                max(0.0, min(100.0, 100.0 * (1.0 - idle / total))) if total > 0 else 0.0
            )

    def stats(self) -> ResourceStats:
        return ResourceStats(
            sum(self.cpu) / len(self.cpu) if self.cpu else 0.0,
            max(self.ram, default=0.0),
            sum(self.ram) / len(self.ram) if self.ram else 0.0,
        )
