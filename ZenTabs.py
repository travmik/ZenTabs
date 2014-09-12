import os
import sys
import shutil
import re
from functools import wraps
import sublime
import sublime_plugin


# temporary because ST2 doesn't have plugin_loaded event
def sublime_text_3():
    """Returns True if this is Sublime Text 3
    """
    try:
        return int(sublime.version()) >= 3000
    except ValueError:
        return sys.hexversion >= 0x030000F0

if not sublime_text_3():
    from TabsWorker import is_active
    from TabsWorker import WindowSet, WindowTabs
else:
    from .TabsWorker import is_active
    from .TabsWorker import WindowSet, WindowTabs


g_tabLimit = 50
g_showFullPath = False
g_selectedItems = 1
is_debug_enabled = False
win_set = WindowSet()
win_tabs = WindowTabs(-1)


def plugin_loaded():
    global g_tabLimit
    global g_showFullPath
    global is_debug_enabled
    settings = sublime.load_settings('ZenTabs.sublime-settings')
    g_tabLimit = settings.get('open_tab_limit', g_tabLimit)
    g_showFullPath = settings.get('show_full_path', g_showFullPath)
    is_debug_enabled = settings.get('debug', is_debug_enabled)
    highlight_modified_tabs = settings.get('highlight_modified_tabs', -1)
    if highlight_modified_tabs != -1:
        global_settings = sublime.load_settings("Preferences.sublime-settings")
        global_settings.set("highlight_modified_tabs", highlight_modified_tabs)
        sublime.save_settings("Preferences.sublime-settings")
    print("Limit: " + str(g_tabLimit))
    print("Full path: " + str(g_showFullPath))
    print("Highlight: " + str(highlight_modified_tabs))


if not sublime_text_3():
    # because of plugin loaded earlier than preferences
    sublime.set_timeout(lambda: plugin_loaded(), 500)


def Logger(function=None, msg="Debug", full=True):
    def LOG(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            responce = function(*args, **kwargs)
            if is_debug_enabled:
                print("======== " + str(msg) + " ========")
                if full:
                    print("window id", win_tabs.win_id)
                    print("e_tabs", " ".join(str(v_id) for v_id in win_tabs.edited_tab_ids))
                    print("o_tabs", " ".join(str(v_id) for v_id in win_tabs.opened_tab_ids))
                    print("f_tabs", " ".join(str(v_id) for v_id in win_tabs.favorited_tab_ids))
                    print("w_tabs", " ".join(str(v.id()) for v in sublime.active_window().views()))
            return responce

        return wrapper

    if not function:  # User passed in a name argument
        def waiting_for_func(function):
            return LOG(function)
        return waiting_for_func
    else:
        return LOG(function)


class ZenTabsListener(sublime_plugin.EventListener):

    @Logger(msg="on_close")
    def on_close(self, view):
        win_tabs.remove_from_lists(view.id())

    @Logger(msg="on_activated")
    def on_activated(self, view):
        global win_tabs
        if sublime.active_window() and sublime.active_window().id() != win_tabs.win_id:
            win_tabs = win_set.get_current_window_tab(sublime.active_window())

        sublime.set_timeout(lambda: self.process(view.id()), 200)

    @Logger(msg="on_post_save")
    def on_post_save(self, view):
        win_tabs.renew_on_modify(view)

    @Logger(msg="on_modified")
    def on_modified(self, view):
        win_tabs.renew_on_modify(view)

    def process(self, view_id):
        win_tabs.renew_on_activate(view_id)
        win_tabs.close_tabs_if_needed(g_tabLimit, view_id)

    def set_tabs_visibility(self):
        if len(sublime.active_window().views()) == 1:
            sublime.active_window().run_command('toggle_tabs')


class ZenTabsFavoritsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        win_tabs.toggle_fav_list(sublime.active_window().active_view().id())

    def run_1(self, edit):
        real_theme = sublime.active_window().active_view().settings().get('color_scheme')
        theme = os.path.join("..", "..", real_theme)
        print(theme)
        dir_name = os.path.join(os.path.dirname(theme))
        file_name = "#fav#" + os.path.basename(theme)
        fav_theme = os.path.join(dir_name, file_name)

        print(file_name)
        print(dir_name)
        print(os.getcwd())

        shutil.copy(theme, fav_theme)

        my_file = open(fav_theme, "r")
        lines_of_file = my_file.readlines()
        for index, line in enumerate(lines_of_file):
            if line.find("background") != -1:
                bg_color_line = lines_of_file[index+1]
                lines_of_file.remove(bg_color_line)
                m = re.match(r".*<string>(#.+)</string>.*", bg_color_line)
                hex_color = m.group(1)
                rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
                new_rgb_int = [int(hex_value, 16) + 5 for hex_value in rgb_hex]
                # make sure new values are between 0 and 255
                new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int]
                # hex() produces "0x88", we want just "88"
                hex_color = "#%02x%02x%02x" % tuple(new_rgb_int)
                print(new_rgb_int)
                print(hex_color)
                lines_of_file.insert(index+1, "<string>" + hex_color + "</string>\n")
                break

        fav_file = open(fav_theme, "w")
        fav_file.write("".join(lines_of_file))
        fav_file.close()

        # sublime.active_window().active_view().settings().set('color_scheme',
        #     os.path.join(os.path.dirname(real_theme), file_name))


class ZenTabsReloadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        plugin_loaded()


class SwitchTabsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.window = sublime.active_window()
        self.active_view = self.window.active_view()
        self.name_list = []
        self.view_list = []

        view_ids = reversed(win_tabs.edited_tab_ids)
        self.prepare_lists(view_ids)
        view_ids = reversed(win_tabs.opened_tab_ids)
        self.prepare_lists(view_ids)

        self.window.run_command("hide_overlay")
        self.window.show_quick_panel(self.name_list, self.on_done, False, g_selectedItems)
        self.next_item(len(self.name_list))

    def prepare_lists(self, view_ids):
        for view_id in view_ids:
            view = win_tabs.get_view_by_id(view_id)
            if not view:
                win_tabs.remove_from_lists(view_id)
                break

            is_current = is_active(view)
            is_draft = view.file_name() is None

            if is_draft:
                name = view.name()
                #set the view name to untitled if we get an empty name
                if len(name) == 0:
                    name = "untitled"
            else:
                name = os.path.basename(view.file_name())

            if is_current:
                name += "\t^"  # current
            if not view.file_name() or view.is_dirty():
                name += "\t*"  # unsaved
            if view.is_read_only():
                name += "\t#"  # read only

            self.add_element(is_current, self.view_list, view)
            if g_showFullPath and not is_draft:
                caption = os.path.dirname(view.file_name())
                self.add_element(is_current, self.name_list, [name, caption])
            else:
                self.add_element(is_current, self.name_list, [name])

    def next_item(self, list_size):
        global g_selectedItems
        if g_selectedItems >= list_size - 1:
            g_selectedItems = 0
        else:
            g_selectedItems += 1

    def on_done(self, index):
        global g_selectedItems
        if index > -1:
            g_selectedItems = 1
            sublime.active_window().focus_view(self.view_list[index])
        self.name_list = []
        self.view_list = []

    def add_element(self, is_current, list, element):
        if is_current:
            list.insert(0, element)
        else:
            list.append(element)
