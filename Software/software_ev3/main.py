#!/usr/bin/env pybricks-micropython
from controllers.controller import Controller

def main():
    # Create controller and start behavior
    controller1 = Controller()
    controller2 = Controller()

    if controller1 is controller2:
        print("it worked")
    controller1.run()

if __name__ == "__main__":
    main()