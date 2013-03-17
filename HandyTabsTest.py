from unittest import TestCase
import unittest 
from mock import MagicMock
from mock import patch

class TestGoodMyModule(TestCase):

	def setUp(self):
		self.sublime_mock = MagicMock()
		self.sublime_mock.sublime.log.return_value		
		self.sublime_plugin_mock = MagicMock()
		self.sublime_plugin_mock.sublime.log.return_value = True
		modules = {
		   	'sublime': self.sublime_mock,
		   	'sublime_plugin': self.sublime_plugin_mock
		}	 
		self.module_patcher = patch.dict('sys.modules', modules)
		self.module_patcher.start()		
		from HandyTabs import HandyTabsListener
		self.my_module = HandyTabsListener()	

	def tearDown(self):
		self.module_patcher.stop()	

   	def test_hello_should_say_waitforit_hello(self):
   		print "Yaeh!!!!"
		m = self.my_module()


class SublimeMock(object):
	def load_settings(param):
		return "None"

if __name__ == '__main__':
    unittest.main()