import sublime

class WindowTabs(object):
    opened_tab_ids = []
    edited_tab_ids = [] 
    def add_to_opened(self, view_id):
        if view_id not in self.edited_tab_ids:
            self.renew_list(self.opened_tab_ids, view_id)   
            
    def add_to_modified(self, view_id):
        self.renew_list(self.edited_tab_ids, view.id())
        self.remove_from_list(self.opened_tab_ids, view.id())  

    def remove_from_list(self, p_list, view_id):
        if view_id in p_list:
            p_list.remove(view_id)  

    def renew_list(self, p_list, view_id):
        if self.get_view_by_id(view_id) is not None:
            if view_id in p_list:
                p_list.append(p_list.pop(p_list.index(view_id)))
            else:
                p_list.append(view_id)  

    def get_view_by_id(self, view_id):
        view = None
        window = sublime.active_window()
        if window is not None:
            for v in sublime.active_window().views():
                if v.id() == view_id:
                    view = v
                    break
        return view

class WindowSet(object):
    window_set = {}

    def add_window(self, win_id):
        if win_id not in window_set:
            window_set[win_id] = []