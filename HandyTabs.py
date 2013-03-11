import sublime, sublime_plugin

g_setting = sublime.load_settings('handytabs.sublime-settings')

g_tabLimit = g_setting.get('open_tab_limit', 10)



class HandyTabsListener(sublime_plugin.EventListener):
	window_id = 0	
	opened_tab_ids = []
	edited_tab_ids = []

	def on_close(self, view):
		self.remove_from_list(view.id())

	def on_activated(self, view):
		if sublime.active_window().id() != self.window_id:
			print("window changed")
			self.opened_tab_ids = [view.id() for view in sublime.active_window().views()]
			self.window_id = sublime.active_window().id()
		sublime.set_timeout(lambda: self.process(view.id()), 200)
		
	def on_post_save(self, view):
		if view.id() in self.edited_tab_ids:
			self.edited_tab_ids.remove(view.id())
		self.renew_list(view.id())




	def process(self, view_id):
		self.renew_list(view_id)
		if len(sublime.active_window().views()) - len(self.edited_tab_ids) > g_tabLimit:
			self.close_last_tab()

	def close_last_tab(self):
		index = 0
		active_window = sublime.active_window()
		while len(active_window.views()) - len(self.edited_tab_ids) > g_tabLimit:
			view_id = self.opened_tab_ids[index]
			view = self.get_view_by_id(view_id)
			self.remove_from_list(view_id)

			if view:
				if not view.is_dirty() and not view.is_scratch():
					active_window.focus_view(view)
					active_window.run_command('close')
				else:
					self.edited_tab_ids.append(view_id)

			if index < g_tabLimit:
				index += 1
			else:
				break
			

	def remove_from_list(self, view_id):
		print view_id
		if view_id in self.opened_tab_ids:
			self.opened_tab_ids.remove(view_id)

	def get_view_by_id(self, view_id):
		view = None
		for v in sublime.active_window().views():
			if v.id() == view_id:
				view = v
				break
		return view


	def renew_list(self, view_id):
		if self.get_view_by_id(view_id) is not None: 
			if view_id in self.opened_tab_ids:
				self.opened_tab_ids.append(self.opened_tab_ids.pop(self.opened_tab_ids.index(view_id)))
			else:
				self.opened_tab_ids.append(view_id)
		print "u_tabs", " ".join(str(v_id) for v_id in self.edited_tab_ids)
		print "o_tabs", " ".join(str(v_id) for v_id in self.opened_tab_ids)
		print "w_tabs", " ".join(str(v.id()) for v in sublime.active_window().views())