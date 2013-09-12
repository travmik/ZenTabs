import sublime, sublime_plugin
import LogUtils
from LogUtils import Logger
from TabsWorker import WindowTabs
import os


g_tabLimit = 50
g_showFullPath = False
win_tabs = WindowTabs()
def plugin_loaded():
    global g_tabLimit
    global g_showFullPath
    settings = sublime.load_settings('zentabs.sublime-settings')
    g_tabLimit = settings.get('open_tab_limit', g_tabLimit)
    g_showFullPath = settings.get('show_full_path', g_showFullPath)
    highlight_modified_tabs = settings.get('highlight_modified_tabs', -1)
    if highlight_modified_tabs != -1:
        global_settings = sublime.load_settings("Preferences.sublime-settings")
        global_settings.set("highlight_modified_tabs", highlight_modified_tabs)
        sublime.save_settings("Preferences.sublime-settings")
    
# temporary because ST2 doesn't have plugin_loaded event
if int(sublime.version()) < 3000:
    plugin_loaded()
    LogUtils.plugin_loaded()

def is_preview(view):
    return sublime.active_window().get_view_index(view)[1] == -1


def is_active(view):
    return view.id() == sublime.active_window().active_view().id()

def is_edited(view):
    return view.is_dirty() or view.is_scratch()


def is_closable(view):
    is_not_closable = is_edited() \
                    or is_preview(view) \
                    or is_active(view) \
                    or view.is_loading()
                    
    return not(is_not_closable)


class ZenTabsReloadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        plugin_loaded()
        LogUtils.plugin_loaded()


g_selectedItems = 1
class SwitchTabsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.window = sublime.active_window()
        self.active_view = self.window.active_view()
        self.name_list = []
        self.view_list = []
        
        view_ids = reversed(win_tabs.opened_tab_ids)
        self.prepare_lists(view_ids)
        view_ids = reversed(win_tabs.edited_tab_ids)
        self.prepare_lists(view_ids)

        self.window.run_command("hide_overlay")
        self.window.show_quick_panel(self.name_list, self.on_done, False, g_selectedItems)
        self.next_item(len(self.name_list))

    def prepare_lists(self, view_ids):
        for view_id in view_ids:
            view = win_tabs.get_view_by_id(view_id)
            if view.file_name() is None:
                name = view.name()
                #set the view name to untitled if we get an empty name
                if len(name) == 0:
                    name = "untitled"
            else:
                if g_showFullPath:
                    name = view.file_name()
                else: 
                    name = os.path.basename(view.file_name())

            # check if this name is already in use, and if so, try to append 
            if not g_showFullPath:
                for entry in self.name_list:
                    if entry[0] == name:
                        index = self.name_list.index(entry)
                        if self.view_list[index].file_name() is not None:
                            self.name_list[index][0] = self.view_list[index].file_name()
                        if view.file_name() is not None:
                            name = view.file_name()

            if self.window.get_view_index(self.active_view) == self.window.get_view_index(view):
                name += "\t^" #current
            if view.file_name() is None or view.is_dirty():
                name += "\t*" #unsaved
            if view.is_read_only():
                name += "\t#" #read only

            self.view_list.append(view)
            self.name_list.append([name])

    def next_item(self, list_size):
        global g_selectedItems
        if g_selectedItems >= list_size - 1: 
            g_selectedItems = 1
        else: 
            g_selectedItems += 1

    def on_done(self, index):
        global g_selectedItems
        if index > - 1:
            g_selectedItems = 1
            sublime.active_window().focus_view(self.view_list[index])
        self.name_list = []
        self.view_list = []


class ZenTabsListener(sublime_plugin.EventListener):
    window_id = 0

    @Logger(msg = "on_close")
    def on_close(self, view):
        win_tabs.remove_from_list(win_tabs.opened_tab_ids, view.id())

    @Logger(msg = "on_activated")
    def on_activated(self, view):
        if sublime.active_window() is not None and sublime.active_window().id() != self.window_id:
            self.window_id = sublime.active_window().id()
            
            win_tabs.opened_tab_ids, win_tabs.edited_tab_ids = [], []
            for view in sublime.active_window().views():
                if is_edited(view):
                    win_tabs.renew_list(win_tabs.edited_tab_ids, view.id())
                else :
                    win_tabs.renew_list(win_tabs.opened_tab_ids, view.id())
            
        sublime.set_timeout(lambda: self.process(view.id()), 200)

    @Logger(msg = "on_post_save")
    def on_post_save(self, view):
        win_tabs.remove_from_list(win_tabs.edited_tab_ids, view.id())
        win_tabs.renew_list(win_tabs.opened_tab_ids, view.id())

    @Logger(msg = "on_modified")
    def on_modified(self, view):
        if view.is_dirty():
            win_tabs.renew_list(win_tabs.edited_tab_ids, view.id())
            win_tabs.remove_from_list(win_tabs.opened_tab_ids, view.id())
        else:
            win_tabs.renew_list(win_tabs.opened_tab_ids, view.id())
            win_tabs.remove_from_list(win_tabs.edited_tab_ids, view.id())

    def process(self, view_id):
        if view_id not in win_tabs.edited_tab_ids:
            win_tabs.renew_list(win_tabs.opened_tab_ids, view_id)
        if len(sublime.active_window().views()) - len(win_tabs.edited_tab_ids) > g_tabLimit:
            self.close_last_tab()

    def close_last_tab(self):
        index = 0
        active_window = sublime.active_window()
        while len(active_window.views()) - len(win_tabs.edited_tab_ids) > g_tabLimit:
            view_id = win_tabs.opened_tab_ids[index]
            view = win_tabs.get_view_by_id(view_id)
            win_tabs.remove_from_list(win_tabs.opened_tab_ids, view_id)

            if view:
                if not view.is_dirty() and not view.is_scratch():
                    active_window.focus_view(view)
                    active_window.run_command('close')
                else:
                    win_tabs.edited_tab_ids.append(view_id)

            if index < len(win_tabs.opened_tab_ids):
                index += 1
            else:
                break

    #for tests
    def currentWindow(self):
        return win_tabs