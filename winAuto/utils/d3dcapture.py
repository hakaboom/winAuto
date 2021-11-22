# -*- coding: utf-8 -*-
# rotypes与d3d从https://github.com/dantmnf的库中截取而来
import ctypes
import ctypes.wintypes
from winAuto.utils.rotypes.roapi import GetActivationFactory
from winAuto.utils.rotypes.Windows.Foundation import TypedEventHandler
from winAuto.utils.rotypes.inspectable import IInspectable

from winAuto.utils.rotypes.Windows.Graphics.Capture import Direct3D11CaptureFramePool, IGraphicsCaptureItemInterop, \
    IGraphicsCaptureItem, GraphicsCaptureItem
from winAuto.utils.rotypes.Windows.Graphics.DirectX import DirectXPixelFormat
from winAuto.utils.rotypes.Windows.Graphics.DirectX.Direct3D11 import IDirect3DDxgiInterfaceAccess, \
    CreateDirect3D11DeviceFromDXGIDevice, IDirect3DDevice

from . import d3d11


import numpy as np

PBYTE = ctypes.POINTER(ctypes.c_ubyte)


class CaptureSession(object):
    def __init__(self):
        self._rtdevice = IDirect3DDevice()
        self._dxdevice = d3d11.ID3D11Device()
        self._immediatedc = d3d11.ID3D11DeviceContext()
        self._framepool = None
        self._session = None
        self._item = None
        self._last_size = None
        self.frame_callback = None
        self.close_callback = None

    def _create_device(self):
        d3d11.D3D11CreateDevice(
            None,
            d3d11.D3D_DRIVER_TYPE_HARDWARE,
            None,
            d3d11.D3D11_CREATE_DEVICE_BGRA_SUPPORT,
            None,
            0,
            d3d11.D3D11_SDK_VERSION,
            ctypes.byref(self._dxdevice),
            None,
            ctypes.byref(self._immediatedc)
        )
        self._rtdevice = CreateDirect3D11DeviceFromDXGIDevice(self._dxdevice)
        self._evtoken = None

    def start(self, hwnd, capture_cursor=False):
        self.stop()
        self._create_device()
        interop = GetActivationFactory('Windows.Graphics.Capture.GraphicsCaptureItem').astype(IGraphicsCaptureItemInterop)
        item = interop.CreateForWindow(hwnd, IGraphicsCaptureItem.GUID)
        self._item = item
        self._last_size = item.Size
        delegate = TypedEventHandler(GraphicsCaptureItem, IInspectable).delegate(
            self._closed_callback)
        self._evtoken = item.add_Closed(delegate)
        self._framepool = Direct3D11CaptureFramePool.CreateFreeThreaded(self._rtdevice, DirectXPixelFormat.B8G8R8A8UIntNormalized,
                                                                                                         1, item.Size)
        self._session = self._framepool.CreateCaptureSession(item)
        pool = self._framepool
        pool.add_FrameArrived(
            TypedEventHandler(Direct3D11CaptureFramePool, IInspectable).delegate(
                self._frame_arrived_callback))
        self._session.IsCursorCaptureEnabled = capture_cursor
        self._session.StartCapture()

    def _frame_arrived_callback(self, x, y):
        if self.frame_callback is not None:
            self.frame_callback(self)

    def _closed_callback(self, x, y):
        if self.close_callback is not None:
            self.close_callback(self)
        self.stop()

    def stop(self):
        if self._framepool is not None:
            self._framepool.Close()
            self._framepool = None
        if self._session is not None:
            # self._session.Close()  # E_UNEXPECTED ???
            self._session = None
        self._item = None
        self._rtdevice.Release()
        self._dxdevice.Release()

    def _reset_framepool(self, size, reset_device=False):
        if reset_device:
            self._create_device()
        self._framepool.Recreate(self._rtdevice,
                                 DirectXPixelFormat.B8G8R8A8UIntNormalized, 1, size)

    def get_frame(self):
        frame = self._framepool.TryGetNextFrame()
        if not frame:
            return None
        img = None
        with frame:
            need_reset_framepool = False
            need_reset_device = False
            if frame.ContentSize.Width != self._last_size.Width or frame.ContentSize.Height != self._last_size.Height:
                # print('size changed')
                need_reset_framepool = True
                self._last_size = frame.ContentSize

            if need_reset_framepool:
                self._reset_framepool(frame.ContentSize)
                return self.get_frame()
            tex = None
            cputex = None
            try:
                tex = frame.Surface.astype(IDirect3DDxgiInterfaceAccess).GetInterface(
                    d3d11.ID3D11Texture2D.GUID).astype(d3d11.ID3D11Texture2D)
                desc = tex.GetDesc()
                desc2 = d3d11.D3D11_TEXTURE2D_DESC()
                desc2.Width = desc.Width
                desc2.Height = desc.Height
                desc2.MipLevels = desc.MipLevels
                desc2.ArraySize = desc.ArraySize
                desc2.Format = desc.Format
                desc2.SampleDesc = desc.SampleDesc
                desc2.Usage = d3d11.D3D11_USAGE_STAGING
                desc2.CPUAccessFlags = d3d11.D3D11_CPU_ACCESS_READ
                desc2.BindFlags = 0
                desc2.MiscFlags = 0
                cputex = self._dxdevice.CreateTexture2D(ctypes.byref(desc2), None)
                self._immediatedc.CopyResource(cputex, tex)
                mapinfo = self._immediatedc.Map(cputex, 0, d3d11.D3D11_MAP_READ, 0)
                img = np.ctypeslib.as_array(ctypes.cast(mapinfo.pData, PBYTE), (desc.Height, mapinfo.RowPitch // 4, 4))[
                      :, :desc.Width].copy()
                self._immediatedc.Unmap(cputex, 0)
            except OSError as e:
                if e.winerror == d3d11.DXGI_ERROR_DEVICE_REMOVED or e.winerror == d3d11.DXGI_ERROR_DEVICE_RESET:
                    need_reset_framepool = True
                    need_reset_device = True
                else:
                    raise
            finally:
                if tex is not None:
                    tex.Release()
                if cputex is not None:
                    cputex.Release()
            if need_reset_framepool:
                self._reset_framepool(frame.ContentSize, need_reset_device)
                return self.get_frame()
        return img
