import unittest
from unittest import TestCase


if __name__ == '__main__':
    from mock import MagicMock
    from mock import patch

    class ViewMock(MagicMock):
        _id = 0
        _dirty = False
        _scratch = False

        def id(self):
            return self._id

        def is_dirty(self):
            return self._dirty

        def is_scratch(self):
            return self._scratch

    class WindowMock(ViewMock):
        _views = []
        _focused_view = None

        def views(self):
            return self._views

        def focus_view(self, view):
            self._focused_view = view

        def run_command(self, command):
            if command is 'close' and self._focused_view is not None:
                self._views.remove(self._focused_view)
                self._focused_view = None

    class SublimeMock(object):
        sublime = MagicMock()
        EventListener = object().__class__
        TextCommand = object().__class__
        active_window = WindowMock()
        active_window._id = 123

        def load_settings(self, param):
            return {"open_tab_limit": 10}

        def set_timeout(testObj, func, timeout):
            func()

        def version(self):
            return 2129

    class TestZenTabs(TestCase):

        def setUp(self):
            self.sublime_mock = SublimeMock()
            self.sublime_mock.sublime.log.return_value
            self.sublime_plugin_mock = SublimeMock()
            self.sublime_plugin_mock.sublime.log.return_value = True
            modules = {
                'sublime': self.sublime_mock,
                'sublime_plugin': self.sublime_plugin_mock
            }
            self.module_patcher = patch.dict('sys.modules', modules)
            self.module_patcher.start()

            from ZenTabs import ZenTabsListener
            self.tabs_mock = ZenTabsListener()

        def tearDown(self):
            self.module_patcher.stop()

        def test1(self):
            for i in range(10):
                self.activate(i)
            self.printStat("opened 10 tabs[0...9]")

            self.close(1)
            self.printStat("closed view with id=1")

            self.activate(2)
            self.printStat("activated view with id=2")

            for i in range(10, 13):
                self.activate(i)
            self.printStat("opened more 3 tabs[10...12]")

            self.modify(4)
            self.printStat("modifyed view with id=4")

            self.modify(5)
            self.modify(6)
            self.modify(7)
            self.modify(8)
            self.modify(9)
            self.modify(2)
            self.modify(10)
            self.modify(11)
            self.modify(12)
            self.printStat("modifyed all 10 views")

            self.activate(13)
            self.printStat("opened one more view with id 13")

        def close(self, view_id):
            view = self.get_view_by_id(view_id)
            if view is not None:
                self.sublime_mock.active_window.views().remove(view)
                self.tabs_mock.on_close(view)

        def activate(self, view_id):
            view = self.get_view_by_id(view_id)
            if view is None:
                view = ViewMock()
                view._id = view_id
                self.sublime_mock.active_window.views().append(view)
            self.tabs_mock.on_activated(view)

        def modify(self, view_id):
            view = self.get_view_by_id(view_id)
            if view is not None:
                view._dirty = True
                self.tabs_mock.on_modified(view)

        def get_view_by_id(self, view_id):
            view = None
            for v in self.sublime_mock.active_window.views():
                if v.id() == view_id:
                    view = v
                    break
            return view

        def printStat(self, msg):
            if msg:
                print(msg)
            from ZenTabs import win_tabs
            print("u_tabs", " ".join(str(v_id) for v_id in win_tabs.edited_tab_ids))
            print("o_tabs", " ".join(str(v_id) for v_id in win_tabs.opened_tab_ids))
            print("w_tabs", " ".join(str(v.id()) for v in self.sublime_mock.active_window().views()))

if __name__ == '__main__':
    unittest.main()
