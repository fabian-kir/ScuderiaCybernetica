from hardware.drive_motor import DriveMotor


def main():
    motor = DriveMotor()
    motor.run_slope_calibration()

if __name__ == '__main__':
    main()