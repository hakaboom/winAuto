



from winAuto.win import Win
import win32api, win32gui
print(Win.get_all_hwnd())
hwnd = 134616

print(f'windowRect : {win32gui.GetWindowRect(hwnd)}')
print(f'clientRect : {win32gui.GetClientRect(hwnd)}')

info = GetWindowInfo(hwnd)
print(f'rcWindow: {info.rcWindow.left} {info.rcWindow.top} {info.rcWindow.right} {info.rcWindow.bottom}')
print(f'rcClient: {info.rcClient.left} {info.rcClient.top} {info.rcClient.right} {info.rcClient.bottom}')

print(win32gui.ScreenToClient(hwnd, (0, 0)))

print(Win(handle_title='retire').rect)