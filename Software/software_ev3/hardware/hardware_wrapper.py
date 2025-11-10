class HardwareWrapper:
    _instance = None

    def __new__(cls):
        from controllers.controller import Controller

        if cls._instance is not None:
            return cls._instance

        instance = super().__new__(cls)
        cls._instance = instance
        Controller().register_update_handler(instance.update)
        return instance

    def update(self, dt):
        raise Exception("this is an abstract method")