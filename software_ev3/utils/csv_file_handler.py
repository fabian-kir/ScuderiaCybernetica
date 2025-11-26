import os

_HAS_OS_PATH = hasattr(os, "path")


class CSVFileHandler:
    def __init__(self, filename, mode='r'):
        # Ensure mode is valid ('r', 'w', 'a')
        if mode not in ('r', 'w', 'a'):
            raise ValueError("Mode must be 'r', 'w', or 'a'")
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        # Open the file using built-in open()
        if self.mode in ('w', 'a'):
            directory = self._dirname(self.filename)
            if directory:
                self._ensure_directory(directory)
        try:
            self.file = open(self.filename, mode=self.mode, newline='')
        except TypeError:
            # MicroPython's open() implementation does not accept the newline argument.
            self.file = open(self.filename, self.mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure file is closed properly
        if self.file:
            self.file.close()

    def write_row(self, row):
        """Write a single list or tuple as a CSV row."""
        if not isinstance(row, (list, tuple)):
            raise TypeError("Row must be a list or tuple")
        line = ",".join(str(item) for item in row)
        self.file.write(line + "\n")

    def write(self, data):
        """Write list, nested list, or string to CSV."""
        if isinstance(data, (list, tuple)):
            # Check if nested
            if all(isinstance(x, (list, tuple)) for x in data):
                for row in data:
                    self.write_row(row)
            else:
                self.write_row(data)
        elif isinstance(data, str):
            self.file.write(data + "\n")
        else:
            raise TypeError("Unsupported data type for writing")

    def read(self):
        """Read entire CSV file into a list of lists."""
        lines = self.file.readlines()
        result = []
        for line in lines:
            line = line.strip()
            if line:  # skip empty lines
                result.append(line.split(","))
        return result

    def read_flat(self):
        """Read a CSV as a flat list (if it’s a single-row file)."""
        data = self.read()
        if len(data) == 1:
            return data[0]
        return data

    def write_dict(self, rows, headers=None):
        """
        Write iterable rows to CSV, optionally with headers.
        Supports rows as dicts or sequences.
        """
        if rows is None:
            return

        rows = list(rows)
        if not rows:
            return

        sample = rows[0]
        # Determine headers and normalization strategy
        if isinstance(sample, dict):
            fieldnames = headers or list(sample.keys())
            self.write_row(fieldnames)
            for row in rows:
                self.write_row([row.get(field, "") for field in fieldnames])
        else:
            if headers:
                self.write_row(headers)
            for row in rows:
                self.write_row(row)

    def read_dict(self):
        """
        Read CSV content as list of dictionaries when headers are present.
        Falls back to list of rows if the file has no header.
        """
        self.file.seek(0)
        rows = self.read()

        if not rows:
            return []

        header = rows[0]
        has_alpha = any(any(ch.isalpha() for ch in cell) for cell in header)
        if header and has_alpha:
            # Treat first row as header
            normalized_rows = []
            for row in rows[1:]:
                normalized = {}
                for idx, field in enumerate(header):
                    normalized[field] = row[idx] if idx < len(row) else ""
                normalized_rows.append(normalized)
            return normalized_rows

        return rows

    def _dirname(self, path):
        if not path:
            return ""
        if _HAS_OS_PATH:
            try:
                return os.path.dirname(path)
            except AttributeError:
                pass
        return self._portable_dirname(path)

    @staticmethod
    def _portable_dirname(path):
        normalized = path.replace("\\", "/")
        if "/" not in normalized:
            return ""
        return normalized.rsplit("/", 1)[0]

    def _ensure_directory(self, directory):
        if not directory:
            return

        makedirs = getattr(os, "makedirs", None)
        if callable(makedirs):
            try:
                makedirs(directory, exist_ok=True)
                return
            except TypeError:
                try:
                    makedirs(directory)
                    return
                except OSError:
                    return
            except OSError:
                return

        self._mkdir_recursively(directory)

    def _mkdir_recursively(self, directory):
        normalized = directory.replace("\\", "/")
        if not normalized:
            return

        absolute = normalized.startswith("/")
        parts = [part for part in normalized.split("/") if part]

        if not parts and absolute:
            return

        current_path = "/" if absolute else ""

        for part in parts:
            if current_path in ("", "/"):
                current_path = ("/" if absolute else "") + part if current_path == "" else current_path + part
            else:
                current_path = current_path + "/" + part
            try:
                os.mkdir(current_path)
            except OSError:
                continue