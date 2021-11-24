from winAuto.cap_methods.WindowsGraphicsCapture import WindowGraphicsCapture
from winAuto.win import Win
from winAuto.utils.window import GetWindowInfo
import win32api
import win32gui
from baseImage import IMAGE

print(Win.get_all_hwnd())
hwnd = 1312688
d = Win(hwnd)
print(d.rect)
a = WindowGraphicsCapture(hwnd)
IMAGE(a.screenshot()).save2path('test.png')
print(IMAGE(a.screenshot()).shape)
print(f'windowRect : {win32gui.GetWindowRect(hwnd)}')
print(f'clientRect : {win32gui.GetClientRect(hwnd)}')

info = GetWindowInfo(hwnd)
print(f'rcWindow: {info.rcWindow.left} {info.rcWindow.top} {info.rcWindow.right} {info.rcWindow.bottom}')
print(f'rcClient: {info.rcClient.left} {info.rcClient.top} {info.rcClient.right} {info.rcClient.bottom}')

print(win32gui.ScreenToClient(hwnd, (1607, 1194)))

border = (info.rcWindow.left - info.rcClient.left,
          info.rcWindow.top - info.rcClient.top,
          info.rcWindow.right - info.rcClient.right,
          info.rcWindow.bottom - info.rcClient.bottom)
print(border)
