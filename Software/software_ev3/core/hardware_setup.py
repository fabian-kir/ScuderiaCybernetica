from hardware import BalanceMotor, DistanceSensor, PowerTrain, SlopeSensor
from config.ports import PORTS

def init_hardware():
    hub = PrimeHub()
    hardware = {
        "robot_hub": RobotHub.init(),
        "power_train": PowerTrain.init(PORTS["LEFT_MOTOR"], PORTS["RIGHT_MOTOR"]),
        "balance_motor": BalanceMotor.init(PORTS["BALANCE_MOTOR"]),
        "slope_sensor": SlopeSensor.init(PORTS["COLOR_SENSOR"]),
        "distance_sensor": UltrasonicSensor.init(PORTS["ULTRASONIC_SENSOR"]),
    }
    return hardware