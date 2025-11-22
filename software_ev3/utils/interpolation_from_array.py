class InterpolationFromArray:
    def __init__(self, array):
        # Sort the array by x-value (ascending)
        self.array = sorted(array, key=lambda p: p[0])

    def interpolate(self, x):
        # If x is outside the range, clamp to the nearest boundary
        if x <= self.array[0][0]:
            return self.array[0][1]
        if x >= self.array[-1][0]:
            return self.array[-1][1]

        # Find the correct interval
        for i in range(len(self.array) - 1):
            x1, y1 = self.array[i]
            x2, y2 = self.array[i + 1]
            if x1 <= x <= x2:
                # Linear interpolation
                t = (x - x1) / (x2 - x1)
                return y1 + t * (y2 - y1)

        # Should never reach here if array has valid structure
        raise ValueError("Interpolation failed: x out of bounds.")

class Interpolation2DFromArray:
    def __init__(self, array):
        # Expecting array as list of (x, y, z) tuples
        self.points = sorted(array, key=lambda p: (p[0], p[1]))

    def interpolate(self, x, y):
        # Extract unique sorted x and y values
        xs = sorted(set(p[0] for p in self.points))
        ys = sorted(set(p[1] for p in self.points))

        # Clamp x and y
        x = max(xs[0], min(xs[-1], x))
        y = max(ys[0], min(ys[-1], y))

        # Find bounding x and y values
        for i in range(len(xs) - 1):
            if xs[i] <= x <= xs[i+1]:
                x1, x2 = xs[i], xs[i+1]
                break

        for j in range(len(ys) - 1):
            if ys[j] <= y <= ys[j+1]:
                y1, y2 = ys[j], ys[j+1]
                break

        # Extract z values at the four surrounding points
        def z(xi, yi):
            for p in self.points:
                if p[0] == xi and p[1] == yi:
                    return p[2]
            raise ValueError(f"No data for ({xi}, {yi})")

        Q11 = z(x1, y1)
        Q12 = z(x1, y2)
        Q21 = z(x2, y1)
        Q22 = z(x2, y2)

        # Bilinear interpolation
        denom = (x2 - x1) * (y2 - y1)
        if denom == 0:
            raise ValueError("Degenerate grid cell for interpolation")

        return (
            Q11 * (x2 - x) * (y2 - y) +
            Q21 * (x - x1) * (y2 - y) +
            Q12 * (x2 - x) * (y - y1) +
            Q22 * (x - x1) * (y - y1)
        ) / denom