Feature: Using plugins to create actually running application
  As a user
  In order to influence the behaviour of the program
  I want to specify the loaded plugins

    Scenario: a plugin from Dewi can be loaded
      Given a predefined plugin loader
       When a plugin is loaded
       Then the plugin is listed in the registered plugins
        And its load() method is called

    Scenario: load the sample command plugin as command line
       When the 'sample' command is run from the sample plugin
       Then the application exit status is 42
