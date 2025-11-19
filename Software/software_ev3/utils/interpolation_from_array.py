class InterpolationFromArray:
    def __init__(self, array):
        self.array = array

    def interpolate(self, x):
        # Ensure x is within the bounds of the array
        if x < 0 or x >= len(self.array):
            raise ValueError("x must be within the bounds of the array indices.")

        # If x is an integer, no interpolation is needed
        if x.is_integer():
            return self.array[int(x)]

        # Find the two nearest indices around x
        x1 = int(x)
        x2 = x1 + 1

        # If x1 is the last index, no interpolation is possible
        if x2 >= len(self.array):
            raise ValueError("x is too large for interpolation.")

        # Perform linear interpolation
        y1 = self.array[x1]
        y2 = self.array[x2]
        
        # Calculate interpolated value using the formula
        return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

# Example usage:
array = [1, 3, 7, 11]
interpolator = InterpolationFromArray(array)

# Interpolating between index 1 and 2
print(interpolator.interpolate(1.5))  # Output will be between 3 and 7
