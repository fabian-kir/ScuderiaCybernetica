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