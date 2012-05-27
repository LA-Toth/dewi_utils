from DWA.Core.Command import Command


class CheckoutCommand(Command):
    def _perform_command(self):
        print("Checkout command")
