from unittest import TestCase
import unittest 
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
	active_window = WindowMock()
	active_window._id = 123

	def load_settings(self, param):
		return {"open_tab_limit": 10}

	def set_timeout(testObj, func, timeout):
		func()



class TestHandyTabs(TestCase):

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
		from HandyTabs import HandyTabsListener
		self.tabs_mock = HandyTabsListener()	

	def tearDown(self):
		self.module_patcher.stop()	

   	def test1(self):
		tabListener = self.tabs_mock
		sublime = self.sublime_mock
		
		print "open 10 tabs[0...9]"
		for i in range(10):
			self.activate(i)

		print "close view with id=1"
		self.close(1)

		print "activate view with id=2"
		self.activate(2)

		print "open more 3 tabs[10...12]"
		for i in range(10,13):
			view = ViewMock()
			view._id = i
			sublime.active_window.views().append(view)
			tabListener.on_activated(view)

		print "modify view with id=3"
		view = sublime.active_window.views()[1]
		view._dirty = True
		tabListener.on_modified(view)
		tabListener.on_modified(view)
		tabListener.on_modified(view)

   		print sublime.active_window._id
		print tabListener.opened_tab_ids

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

	def get_view_by_id(self, view_id):
		view = None
		for v in self.sublime_mock.active_window.views():
			if v.id() == view_id:
				view = v
				break
		return view

if __name__ == '__main__':
    unittest.main()