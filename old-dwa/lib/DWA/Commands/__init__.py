def register_selfupdate_command():
    from DWA.Core.State import main_command_registry
    from DWA.Core.CommandRegistry import ClassDescriptorWithModuleAndClassName
    descriptor = ClassDescriptorWithModuleAndClassName('DWA.Commands.SelfUpdate', 'SelfUpdateCommand')
    main_command_registry.register_command_class('selfupdate', descriptor)
    main_command_registry.register_command_class('su', descriptor)
