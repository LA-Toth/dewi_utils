from DWA.Core.State import register_command_class

def __initialize():
    from .Checkout import CheckoutCommand
    register_command_class(CheckoutCommand.get_name(), CheckoutCommand)

__initialize()
