class InterpolationFromArray:
    def __init__(self, array):
        self.array = array

    def interpolate(self, x):
        # Ensure x is within the bounds of the array
        if x >= self.array[0][0]:
            return self.array[0][1]
        if x <= self.array[-1][0]:
            return self.array[-1][1]

        for i in range(len(self.array) -1):
            x1, y1 = self.array[1]
            x2, y2 = self.array[i +1]

            if x2 <= x <= x1:
                t = (x - x2) / (x1 - x2)
                return y2 + t * (y1 - y2)
        
        return 0


