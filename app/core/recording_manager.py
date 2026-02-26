from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RecordingSession:
    session_dir: Path
    data_csv_path: Path
    meta_json_path: Path


class RecordingManager:
    def __init__(self) -> None:
        self._session: RecordingSession | None = None
        self._file = None
        self._writer: csv.writer | None = None
        self._rows_written = 0

    @staticmethod
    def default_base_dir() -> Path:
        home = Path(os.path.expanduser("~"))
        return home / "Documents" / "VLoad" / "sessions"

    def start_new_session(self, meta: dict[str, Any], base_dir: Path | None = None) -> RecordingSession:
        self.stop()

        base = base_dir or self.default_base_dir()
        base.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model = str(meta.get("model", "device")).strip().replace(" ", "_")
        safe_id = str(meta.get("id", "")).strip().replace(" ", "_")
        name = f"{stamp}_{safe_model}_{safe_id}" if safe_id else f"{stamp}_{safe_model}"
        session_dir = base / name
        session_dir.mkdir(parents=True, exist_ok=True)

        data_csv_path = session_dir / "data.csv"
        meta_json_path = session_dir / "meta.json"

        meta_json_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        f = open(data_csv_path, "w", newline="", encoding="utf-8")
        writer = csv.writer(f)
        writer.writerow(["时间", "电压(V)", "电流(A)", "功率(W)", "内阻(Ω)"])

        self._file = f
        self._writer = writer
        self._rows_written = 0
        self._session = RecordingSession(session_dir=session_dir, data_csv_path=data_csv_path, meta_json_path=meta_json_path)
        return self._session

    def append(self, ts: str, v: float, i: float, p: float, r: float) -> None:
        if not self._writer or not self._file:
            return
        self._writer.writerow([ts, f"{v:.6f}", f"{i:.6f}", f"{p:.6f}", f"{r:.6f}"])
        self._rows_written += 1
        if self._rows_written % 200 == 0:
            try:
                self._file.flush()
            except Exception:
                pass

    def stop(self) -> None:
        if self._file:
            try:
                self._file.flush()
            except Exception:
                pass
            try:
                self._file.close()
            except Exception:
                pass
        self._file = None
        self._writer = None

    def discard_session(self) -> None:
        session = self._session
        self.stop()
        self._session = None
        if session:
            try:
                import shutil

                shutil.rmtree(session.session_dir, ignore_errors=True)
            except Exception:
                pass

    @property
    def session(self) -> RecordingSession | None:
        return self._session
