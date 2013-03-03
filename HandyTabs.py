import sublime, sublime_plugin

g_setting = sublime.load_settings('handytabs.sublime-settings')

g_tabLimit = g_setting.get('open_tab_limit', 10)


opened_tab_ids = []

class ClearTabsListenerCommand(sublime_plugin.EventListener):

	def on_close(self, view):
		self.remove_from_list(view.id())
		# print "on_close >", view.id()

	def on_activated(self, view):
		sublime.set_timeout(lambda: self.process(view.id()), 200)
		
		# sublime.set_timeout(lambda: self.prin_log(view, "on_activated"), 200)
		


	def prin_log(self, view, action):
		print action, ">", view.id(), view.window()
		print "window views", " ".join(str(v.id()) for v in sublime.active_window().views())


	def process(self, view_id):
		self.renew_list(view_id)
		if len(sublime.active_window().views()) >= g_tabLimit:
			self.close_last_tab()

	def close_last_tab(self):
		index = 0
		active_window = sublime.active_window()
		while len(active_window.views()) > g_tabLimit:
			view_id = opened_tab_ids[index]
			view = self.get_view_by_id(view_id)

			if not view:
				self.remove_from_list(view_id)
			

			if view and not view.is_dirty() and not view.is_scratch():
				self.remove_from_list(view_id)
				active_window.focus_view(view)
				active_window.run_command('close')
				print "close_last_tab closed", view.id()
			elif index < g_tabLimit:
				index += 1
				print "close_last_tab index++"
			else:
				print "close_last_tab break"
				break
		print " ".join(str(v.id()) for v in active_window.views())

	def remove_from_list(self, view_id):
		if view_id in opened_tab_ids:
			print "remove_from_list", view_id
			opened_tab_ids.remove(view_id)

	def get_view_by_id(self, view_id):
		view = None
		for v in sublime.active_window().views():
			if v.id() == view_id:
				view = v
				break
		return view

	def renew_list(self, view_id):
		if self.get_view_by_id(view_id): 
			if view_id in opened_tab_ids:
				opened_tab_ids.insert(-1, opened_tab_ids.pop(opened_tab_ids.index(view_id)))
			else:
				opened_tab_ids.append(view_id)
			print "renew_list", view_id
		print "renew_list", " ".join(str(v_id) for v_id in opened_tab_ids)
		print "window_list", " ".join(str(v.id()) for v in sublime.active_window().views())