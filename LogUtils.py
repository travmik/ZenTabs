import sublime, sublime_plugin
from functools import wraps

is_debug_enabled = False
def plugin_loaded():
    global is_debug_enabled
    settings = sublime.load_settings('zentabs.sublime-settings')
    is_debug_enabled = settings.get('debug', is_debug_enabled)

def Logger(function = None, msg = "Debug", full = True):
    def LOG(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if is_debug_enabled: 
                zen = args[0]
                print("======== " + str(msg) + " ========")
                if True:
                    print("e_tabs", " ".join(str(v_id) for v_id in zen.edited_tab_ids))
                    print("o_tabs", " ".join(str(v_id) for v_id in zen.opened_tab_ids))
                    print("w_tabs", " ".join(str(v.id()) for v in sublime.active_window().views()))
            return function(*args, **kwargs)

        return wrapper

    if not function:  # User passed in a name argument
        def waiting_for_func(function):
            return LOG(function)
        return waiting_for_func

    else:
        return LOG(function)