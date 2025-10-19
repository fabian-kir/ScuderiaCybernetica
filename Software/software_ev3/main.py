from core.hardware_setup import init_hardware
from core import Controller

def main():
    # Initialize all hardware
    hardware = init_hardware()

    # Create controller and start behavior
    controller = Controller.init(hardware)
    controller.run()

if __name__ == "__main__":
    main()