import sublime, sublime_plugin


g_tabLimit = 50
is_debug_enabled = False
def plugin_loaded():
    global g_tabLimit
    global is_debug_enabled
    settings = sublime.load_settings('zentabs.sublime-settings')
    g_tabLimit = settings.get('open_tab_limit', g_tabLimit)
    is_debug_enabled = settings.get('debug', is_debug_enabled)
    highlight_modified_tabs = settings.get('highlight_modified_tabs', -1)
    if highlight_modified_tabs != -1:
        global_settings = sublime.load_settings("Preferences.sublime-settings")
        global_settings.set("highlight_modified_tabs", highlight_modified_tabs)
        sublime.save_settings("Preferences.sublime-settings")
    
# temporary because ST2 doesn't have plugin_loaded event
if int(sublime.version()) < 3000:
    plugin_loaded()

def remove_from_list(p_list, view_id):
    if view_id in p_list:
        p_list.remove(view_id)

def renew_list(p_list, view_id):
    if get_view_by_id(view_id) is not None:
        if view_id in p_list:
            p_list.append(p_list.pop(p_list.index(view_id)))
        else:
            p_list.append(view_id)

def get_view_by_id(view_id):
    view = None
    window = sublime.active_window()
    if window is not None:
        for v in sublime.active_window().views():
            if v.id() == view_id:
                view = v
                break
    return view

class ZenTabsReloadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        plugin_loaded()

class ZenTabsListener(sublime_plugin.EventListener):
    window_id = 0
    opened_tab_ids = []
    edited_tab_ids = []

    def on_close(self, view):
        remove_from_list(self.opened_tab_ids, view.id())
        if is_debug_enabled: self.printStat()

    def on_activated(self, view):
        if sublime.active_window() is not None and sublime.active_window().id() != self.window_id:
            self.window_id = sublime.active_window().id()
            
            self.opened_tab_ids, self.edited_tab_ids = [], []
            for view in sublime.active_window().views():
                if not view.is_dirty() and not view.is_scratch():
                    self.opened_tab_ids.append(view.id())
                if view.is_dirty() and view.is_scratch():
                    self.edited_tab_ids.append(view.id())
            
        sublime.set_timeout(lambda: self.process(view.id()), 200)
        if is_debug_enabled: self.printStat()

    def on_post_save(self, view):
        remove_from_list(self.edited_tab_ids, view.id())
        renew_list(self.opened_tab_ids, view.id())
        if is_debug_enabled: self.printStat()


    def on_modified(self, view):
        if view.is_dirty():
            renew_list(self.edited_tab_ids, view.id())
            remove_from_list(self.opened_tab_ids, view.id())
        else:
            renew_list(self.opened_tab_ids, view.id())
            remove_from_list(self.edited_tab_ids, view.id())
        if is_debug_enabled: self.printStat()


    def process(self, view_id):
        if view_id not in self.edited_tab_ids:
            renew_list(self.opened_tab_ids, view_id)
        if len(sublime.active_window().views()) - len(self.edited_tab_ids) > g_tabLimit:
            self.close_last_tab()

    def close_last_tab(self):
        index = 0
        active_window = sublime.active_window()
        while len(active_window.views()) - len(self.edited_tab_ids) > g_tabLimit:
            view_id = self.opened_tab_ids[index]
            view = get_view_by_id(view_id)
            remove_from_list(self.opened_tab_ids, view_id)

            if view:
                if not view.is_dirty() and not view.is_scratch():
                    active_window.focus_view(view)
                    active_window.run_command('close')
                else:
                    self.edited_tab_ids.append(view_id)

            if index < len(self.opened_tab_ids):
                index += 1
            else:
                break

    def printStat(self):
        print("e_tabs", " ".join(str(v_id) for v_id in self.edited_tab_ids))
        print("o_tabs", " ".join(str(v_id) for v_id in self.opened_tab_ids))
        print("w_tabs", " ".join(str(v.id()) for v in sublime.active_window().views()))