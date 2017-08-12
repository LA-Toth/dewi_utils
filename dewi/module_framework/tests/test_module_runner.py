# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import dewi.tests
from dewi.config.config import Config
from dewi.module_framework.messages import Messages
from dewi.module_framework.module import Module
from dewi.module_framework.module_runner import DuplicatedProvidedModule, ModuleRunner


class TestModuleBase(Module):
    def __init__(self, c=None):
        super().__init__(c or Config(), Messages())
        self.called = False

    def run(self):
        self.called = True
        self.append('_called_', self.provide())


class TestModule1(TestModuleBase):
    def provide(self) -> str:
        return 'tm1'


class TestModule1n(TestModuleBase):
    def provide(self) -> str:
        return 'tm1'


class TestModule2(TestModuleBase):
    def provide(self) -> str:
        return 'tm2'

    def get_filter_tags(self) -> list:
        return ['f1']


class TestModule2n(TestModuleBase):
    def provide(self) -> str:
        return 'tm2'


class TMA(TestModuleBase):
    def provide(self) -> str:
        return 'a'

    def get_filter_tags(self) -> list:
        return ['s']

    def require(self) -> list:
        return ['b', 'd']


class TMB(TestModuleBase):
    def provide(self) -> str:
        return 'b'

    def get_filter_tags(self) -> list:
        return ['s']

    def require(self) -> list:
        return ['e']


class TMC(TestModuleBase):
    def provide(self) -> str:
        return 'b'

    def require(self):
        return ['e']


class TMD(TestModuleBase):
    def provide(self) -> str:
        return 'd'


class TME(TestModuleBase):
    def provide(self) -> str:
        return 'e'


class ModuleRunnerTestBase(dewi.tests.TestCase):
    def set_up(self):
        self.runner = ModuleRunner()

    def _c(self, module_type: type) -> TestModuleBase:
        return self._cc(module_type, None)

    def _cc(self, module_type: type, config) -> TestModuleBase:
        m = module_type(config)
        self.runner.add(m)
        return m


class ModuleRunnerTestWithOneOrTwoModulesAndDifferentTags(ModuleRunnerTestBase):
    def test_runner_without_modules(self):
        try:
            self.runner.run()
        except:
            self.assert_false(True, "Test should not reach this line")

    def test_that_single_module_without_filter_runs_without_Filter(self):
        m = self._c(TestModule1)
        self.runner.run()
        self.assert_true(m.called, "Module run should be called")

    def test_that_single_module_with_filter_does_not_without_Filter(self):
        m = self._c(TestModule2)
        self.runner.run()
        self.assert_false(m.called, "Module run should not be called")

    def test_with_two_modules_one_with_filter(self):
        m1 = self._c(TestModule1)
        m2 = self._c(TestModule2)
        self.runner.run()
        self.assert_true(m1.called, "Module1 run should be called")
        self.assert_false(m2.called, "Module2 run should not be called")

    def test_with_two_modules_and_use_valid_filter_tag(self):
        m1 = self._c(TestModule1)
        m2 = self._c(TestModule2)
        self.runner.run('f1')
        self.assert_true(m1.called, "Module1 run should be called")
        self.assert_true(m2.called, "Module2 run should be called")

    def test_with_two_modules_and_use_invalid_filter_tag_same_as_using_none(self):
        m1 = self._c(TestModule1)
        m2 = self._c(TestModule2)
        self.runner.run('f1-does-not-exist')
        self.assert_true(m1.called, "Module1 run should be called")
        self.assert_false(m2.called, "Module2 run should not be called")


class ModuleRunnerTestWithDuplicatedTags(ModuleRunnerTestBase):
    def test_with_same_tag_but_different_filter_and_run_none_tag(self):
        m1 = self._c(TestModule2)
        m2 = self._c(TestModule2n)
        self.runner.run()
        self.assert_false(m1.called, "Module1 run should not be called")
        self.assert_true(m2.called, "Module2 run should be called")

    def test_with_same_tag_but_different_filter_and_run_filter_tag(self):
        m1 = self._c(TestModule2)
        m2 = self._c(TestModule2n)
        self.runner.run('f1')
        self.assert_true(m1.called, "Module1 run should be called")
        self.assert_false(m2.called, "Module2 run should not be called")

    def test_with_same_module(self):
        m1 = self._c(TestModule1)
        m2 = self._c(TestModule1)
        self.assert_raises(DuplicatedProvidedModule, self.runner.run)

    def test_with_same_tag_and_same_filter_tag(self):
        m1 = self._c(TestModule1)
        m2 = self._c(TestModule1n)
        self.assert_raises(DuplicatedProvidedModule, self.runner.run)


class ModuleRunnerTestWithMultipleModules(ModuleRunnerTestBase):
    def test_with_filter(self):
        cfg = Config()
        ma = self._cc(TMA, cfg)
        mb = self._cc(TMB, cfg)
        mc = self._cc(TMC, cfg)
        md = self._cc(TMD, cfg)
        me = self._cc(TME, cfg)
        self.runner.run('s')
        self.assert_true(ma.called, "Module A run should be called")
        self.assert_true(mb.called, "Module B run should be called")
        self.assert_false(mc.called, "Module C run should not be called")
        self.assert_true(md.called, "Module D run should be called")
        self.assert_true(me.called, "Module E run should be called")

        # It's a valid solution for current implementation
        self.assert_equal(cfg.get('_called_'), ['e', 'b', 'd', 'a'])

    def test_without_filter(self):
        cfg = Config()
        ma = self._cc(TMA, cfg)
        mb = self._cc(TMB, cfg)
        mc = self._cc(TMC, cfg)
        md = self._cc(TMD, cfg)
        me = self._cc(TME, cfg)
        self.runner.run()
        self.assert_false(ma.called, "Module B run should not be called")
        self.assert_false(mb.called, "Module B run should not be called")
        self.assert_true(mc.called, "Module C run should be called")
        self.assert_true(md.called, "Module D run should be called")
        self.assert_true(me.called, "Module E run should be called")

        self.assert_less(cfg.get('_called_').index('e'), cfg.get('_called_').index('b'))
