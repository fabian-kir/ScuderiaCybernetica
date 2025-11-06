#!/usr/bin/env pybricks-micropython
from controllers.controller import Controller

def main():
    # Create controller and start behavior
    controller = Controller()
    controller.run()

if __name__ == "__main__":
    main()