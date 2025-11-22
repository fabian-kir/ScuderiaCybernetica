#!/usr/bin/env pybricks-micropython
from software_ev3.controllers.controller import Controller

def main():
	# Create controller and start behavior
	controller = Controller()
	controller.run()

if __name__ == "__main__":
    main()