from DWA.Core.State import main_command_registry

def __initialize():
    from .Checkout import CheckoutCommand
    main_command_registry.register_command_class(CheckoutCommand.get_name(), CheckoutCommand)

__initialize()
