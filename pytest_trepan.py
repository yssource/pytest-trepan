""" interactive debugging with the Trepan Python Debugger. """
from __future__ import absolute_import
from trepan.api import debug as trepan_debug
import trepan.post_mortem
import sys

import pytest


def pytest_addoption(parser):
    """Adds option --trepan to py.test"""
    group = parser.getgroup("general")
    group._addoption('--trepan',
                     action="store_true", dest="usetrepan", default=False,
                     help="start the trepan Python debugger on errors.")


def pytest_namespace():
    """Allows user code to insert pytest.debug() to enter the trepan debugger"""
    return {'debug': pytestTrepan().debug}


def pytest_configure(config):
    """Called to configure pytest when "pytest --trepan ... " is invoked"""
    if config.getvalue("usetrepan"):
        # 'pdbinvoke' is a magic name?
        config.pluginmanager.register(TrepanInvoke(), 'pdbinvoke')

    old = pytestTrepan._pluginmanager

    def fin():
        pytestTrepan._pluginmanager = old
        pytestTrepan._config = None
    pytestTrepan._pluginmanager = config.pluginmanager
    pytestTrepan._config = config
    config._cleanup.append(fin)


class pytestTrepan:
    """Pseudo Trepan that defers to the real trepan."""
    _pluginmanager = None
    _config = None

    def debug(self):
        """invoke Trepan debugging, dropping any IO capturing."""
        import _pytest.config
        capman = None
        if self._pluginmanager is not None:
            capman = self._pluginmanager.getplugin("capturemanager")
            if capman:
                capman.suspendcapture(in_=True)
            tw = _pytest.config.create_terminal_writer(self._config)
            tw.line()
            tw.sep(">", "Trepan set_trace (IO-capturing turned off)")
            self._pluginmanager.hook.pytest_enter_pdb()
        trepan_debug(level=1)


class TrepanInvoke:
    def pytest_exception_interact(self, node, call, report):
        capman = node.config.pluginmanager.getplugin("capturemanager")
        if capman:
            capman.suspendcapture(in_=True)
        _enter_trepan(node, call.excinfo, report)

    def pytest_internalerror(self, excrepr, excinfo):
        for line in str(excrepr).split("\n"):
            sys.stderr.write("INTERNALERROR> %s\n" % line)
            sys.stderr.flush()
        tb = _postmortem_traceback(excinfo)
        post_mortem(tb)


def _enter_trepan(node, excinfo, rep):
    # XXX we re-use the TerminalReporter's terminalwriter
    # because this seems to avoid some encoding related troubles
    # for not completely clear reasons.
    tw = node.config.pluginmanager.getplugin("terminalreporter")._tw
    tw.line()
    tw.sep(">", "traceback")
    rep.toterminal(tw)
    tw.sep(">", "entering Trepan")
    post_mortem(_postmortem_traceback(excinfo))
    rep._pdbshown = True
    return rep


def _postmortem_traceback(excinfo):
    # A doctest.UnexpectedException is not useful for post_mortem.
    # Use the underlying exception instead:
    from doctest import UnexpectedException
    if isinstance(excinfo.value, UnexpectedException):
        return excinfo.value.exc_info
    else:
        return excinfo._excinfo


def post_mortem(e):
    trepan.post_mortem.post_mortem(e)