from ctypes import windll, create_unicode_buffer


def get_foreground_window_title() -> str:
    window = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(window)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(window, buf, length + 1)
    return buf.value if buf.value else ''


def get_file_content(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        f.close()
    return content
