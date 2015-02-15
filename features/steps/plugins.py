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
def step_impl(context):
    assert 42 == context.plugin_context['test_result']
