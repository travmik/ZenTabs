import sublime


def is_edited(view):
    return view.is_dirty() or view.is_scratch()


def is_preview(view):
    return sublime.active_window().get_view_index(view)[1] == -1


def is_active(view):
    return view.id() == sublime.active_window().active_view().id()


def is_closable(view):
    is_not_closable = is_edited(view) \
                    or is_preview(view) \
                    or is_active(view) \
                    or view.is_loading()
    return not is_not_closable


class WindowTabs(object):
    def __init__(self, win_id):
        self.win_id = win_id
        self.opened_tab_ids = []
        self.edited_tab_ids = []
        self.favorited_tab_ids = []

    def add_to_opened(self, view_id):
        if view_id not in self.edited_tab_ids:
            self.renew_list(self.opened_tab_ids, view_id)

    def renew_on_modify(self, view):
        if view.is_dirty():
            self.renew_modifyed_list(view.id())
            self.remove_from_list(self.opened_tab_ids, view.id())
        else:
            self.renew_opened_list(view.id())
            self.remove_from_list(self.edited_tab_ids, view.id())

    def renew_on_activate(self, view_id):
        if view_id not in self.edited_tab_ids:
            self.renew_opened_list(view_id)
        else:
            self.renew_modifyed_list(view_id)

    def remove_from_lists(self, view_id):
        self.remove_from_list(self.opened_tab_ids, view_id)
        self.remove_from_list(self.edited_tab_ids, view_id)
        self.remove_from_list(self.favorited_tab_ids, view_id)

    def remove_from_opened_list(self, view_id):
        self.remove_from_list(self.opened_tab_ids, view_id)

    def remove_from_list(self, p_list, view_id):
        if view_id in p_list:
            p_list.remove(view_id)

    def renew_opened_list(self, view_id):
        self.renew_list(self.opened_tab_ids, view_id)

    def renew_modifyed_list(self, view_id):
        self.renew_list(self.edited_tab_ids, view_id)

    def renew_list(self, p_list, view_id):
        if self.get_view_by_id(view_id):
            if view_id in p_list:
                p_list.append(p_list.pop(p_list.index(view_id)))
            else:
                p_list.append(view_id)

    def get_view_by_id(self, view_id):
        view = None
        window = sublime.active_window()
        if window:
            for v in sublime.active_window().views():
                if v.id() == view_id:
                    view = v
                    break
        return view

    def get_closable_tabs_count(self):
        return len(self.opened_tab_ids)

    def close_tabs_if_needed(self, g_tabLimit, active_view_id):
        index = 0
        active_window = sublime.active_window()
        while self.get_closable_tabs_count() > g_tabLimit:
            view_id = self.opened_tab_ids[index]
            view = self.get_view_by_id(view_id)

            if not view:
                self.remove_from_lists(view_id)
                continue

            if is_closable(view):
                self.remove_from_opened_list(view_id)
                active_window.focus_view(view)
                active_window.run_command('close')
                if self.get_view_by_id(active_view_id):
                    active_window.focus_view(self.get_view_by_id(active_view_id))

            if index < self.get_closable_tabs_count():
                index += 1
            else:
                break

    def toggle_fav_list(self, view_id):
        if view_id in self.favorited_tab_ids:
            self.favorited_tab_ids.remove(view_id)
        else:
            self.renew_list(self.favorited_tab_ids, view_id)


class WindowSet(object):
    window_set = {}

    def add_window(self, win_id, win_tabs):
        self.window_set[win_id] = win_tabs

    def get_current_window_tab(self, window):
        if window.id() not in self.window_set:
            win_tabs = WindowTabs(window.id())
            for view in window.views():
                if is_edited(view):
                    win_tabs.renew_modifyed_list(view.id())
                else:
                    win_tabs.renew_opened_list(view.id())

            self.add_window(window.id(), win_tabs)
        return self.window_set[window.id()]
