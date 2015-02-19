from dewi.core.application import MainApplication
from dewi.loader.loader import PluginLoader


@given('a predefined plugin loader')
def set_plugin_loader(context):
    context.plugin_loader = PluginLoader()


@when('a plugin is loaded')
def load_plugin(context):
    context.plugin_context = context.plugin_loader.load({'e2elib.PluginTestPlugin'})


@then('the plugin is listed in the registered plugins')
def assert_that_the_plugin_is_listed_in_plugin_loader(context):
    assert 'e2elib.PluginTestPlugin' in context.plugin_loader.loaded_plugins


@then('its load() method is called')
def assert_that_load_method_is_called(context):
    assert 42 == context.plugin_context['test_result']


@when('the \'sample\' command is run from the sample plugin')
def run_main_app_with_sample_command(context):
    app = MainApplication()
    context.result = app.run({'dewi.commands.sample.SamplePlugin'}, ['sample'])


@then('the application exit status is {exit_status}')
def assert_that_app_exit_status_is_the_specified(context, exit_status):
    assert int(exit_status) == context.result
