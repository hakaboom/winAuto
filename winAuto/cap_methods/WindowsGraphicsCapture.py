# -*- coding: utf-8 -*-
from winAuto.utils.d3dcapture import CaptureSession


class WindowGraphicsCapture(object):
    def __init__(self, hwnd: int):
        self._hwnd = hwnd
        self._session = CaptureSession()
        self.state_box = [None, False, False]  # frame, changed, stop

        def frame_callback(_session):
            frame = _session.get_frame()
            if frame is None:
                return
            self.state_box[0] = frame
            self.state_box[1] = True

        def close_callback(_session):
            self.state_box[2] = True

        self._session.frame_callback = frame_callback
        self._session.close_callback = close_callback

        self.start()

    def start(self):
        self._session.start(self._hwnd, True)

    def stop(self):
        self._session.stop()

    def screenshot(self):
        while not self.state_box[2]:
            if self.state_box[1]:
                self.state_box[1] = False
                return self.state_box[0]


