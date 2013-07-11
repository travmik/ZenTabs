import sublime, sublime_plugin


g_tabLimit = 50
def plugin_loaded():
    global g_tabLimit
    settings = sublime.load_settings('zentabs.sublime-settings')
    g_tabLimit = settings.get('open_tab_limit', g_tabLimit)
    
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
    for v in sublime.active_window().views():
        if v.id() == view_id:
            view = v
            break
    return view

class ZenTabsListener(sublime_plugin.EventListener):
    window_id = 0
    opened_tab_ids = []
    edited_tab_ids = []

    def on_close(self, view):
        remove_from_list(self.opened_tab_ids, view.id())

    def on_activated(self, view):
        if sublime.active_window().id() != self.window_id:
            self.window_id = sublime.active_window().id()
            
            self.opened_tab_ids, self.edited_tab_ids = [], []
            for view in sublime.active_window().views():
                if not view.is_dirty() and not view.is_scratch():
                    self.opened_tab_ids.append(view.id())
                if view.is_dirty() and view.is_scratch():
                    self.edited_tab_ids.append(view.id())
            
        sublime.set_timeout(lambda: self.process(view.id()), 200)

    def on_post_save(self, view):
        remove_from_list(self.edited_tab_ids, view.id())
        renew_list(self.opened_tab_ids, view.id())


    def on_modified(self, view):
        if view.is_dirty():
            renew_list(self.edited_tab_ids, view.id())
            remove_from_list(self.opened_tab_ids, view.id())
        else:
            renew_list(self.opened_tab_ids, view.id())
            remove_from_list(self.edited_tab_ids, view.id())



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
        print("u_tabs", " ".join(str(v_id) for v_id in self.edited_tab_ids))
        print("o_tabs", " ".join(str(v_id) for v_id in self.opened_tab_ids))
        print("w_tabs", " ".join(str(v.id()) for v in sublime.active_window().views()))