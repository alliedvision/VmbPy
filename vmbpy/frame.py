"""BSD 2-Clause License

Copyright (c) 2023, Allied Vision Technologies GmbH
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import copy
import ctypes
from typing import Callable, Optional, Tuple, Union

from .c_binding import (PIXEL_FORMAT_TO_LAYOUT, Debayer, FrameStatus, PayloadType, PixelFormat,
                        VmbCError, VmbDebayerMode, VmbError, VmbFrame, VmbFrameFlags, VmbHandle,
                        VmbImage, VmbPixelFormat, VmbTransformInfo, VmbUint8, byref, call_vmb_c,
                        call_vmb_image_transform, decode_flags, sizeof)
from .c_binding.vmb_c import CHUNK_CALLBACK_TYPE
from .error import VmbChunkError, VmbFrameError
from .featurecontainer import FeatureContainer
from .util import Log, RuntimeTypeCheckEnable, TraceEnable, VmbIntEnum

try:
    import numpy  # type: ignore

except ModuleNotFoundError:
    numpy = None  # type: ignore


__all__ = [
    'PixelFormat',
    'MONO_PIXEL_FORMATS',
    'BAYER_PIXEL_FORMATS',
    'RGB_PIXEL_FORMATS',
    'RGBA_PIXEL_FORMATS',
    'BGR_PIXEL_FORMATS',
    'BGRA_PIXEL_FORMATS',
    'YUV_PIXEL_FORMATS',
    'YCBCR_PIXEL_FORMATS',
    'COLOR_PIXEL_FORMATS',
    'OPENCV_PIXEL_FORMATS',
    'FrameStatus',
    'Debayer',
    'Frame',
    'FrameTuple',
    'FormatTuple',
    'intersect_pixel_formats'
]


# Forward declarations
FrameTuple = Tuple['Frame', ...]
FormatTuple = Tuple['PixelFormat', ...]
ChunkCallback = Callable[[FeatureContainer], None]


MONO_PIXEL_FORMATS = (
    PixelFormat.Mono8,
    PixelFormat.Mono10,
    PixelFormat.Mono10p,
    PixelFormat.Mono12,
    PixelFormat.Mono12Packed,
    PixelFormat.Mono12p,
    PixelFormat.Mono14,
    PixelFormat.Mono16
)


BAYER_PIXEL_FORMATS = (
    PixelFormat.BayerGR8,
    PixelFormat.BayerRG8,
    PixelFormat.BayerGB8,
    PixelFormat.BayerBG8,
    PixelFormat.BayerGR10,
    PixelFormat.BayerRG10,
    PixelFormat.BayerGB10,
    PixelFormat.BayerBG10,
    PixelFormat.BayerGR12,
    PixelFormat.BayerRG12,
    PixelFormat.BayerGB12,
    PixelFormat.BayerBG12,
    PixelFormat.BayerGR12Packed,
    PixelFormat.BayerRG12Packed,
    PixelFormat.BayerGB12Packed,
    PixelFormat.BayerBG12Packed,
    PixelFormat.BayerGR10p,
    PixelFormat.BayerRG10p,
    PixelFormat.BayerGB10p,
    PixelFormat.BayerBG10p,
    PixelFormat.BayerGR12p,
    PixelFormat.BayerRG12p,
    PixelFormat.BayerGB12p,
    PixelFormat.BayerBG12p,
    PixelFormat.BayerGR16,
    PixelFormat.BayerRG16,
    PixelFormat.BayerGB16,
    PixelFormat.BayerBG16
)


RGB_PIXEL_FORMATS = (
    PixelFormat.Rgb8,
    PixelFormat.Rgb10,
    PixelFormat.Rgb12,
    PixelFormat.Rgb14,
    PixelFormat.Rgb16
)


RGBA_PIXEL_FORMATS = (
    PixelFormat.Rgba8,
    PixelFormat.Argb8,
    PixelFormat.Rgba10,
    PixelFormat.Rgba12,
    PixelFormat.Rgba14,
    PixelFormat.Rgba16
)


BGR_PIXEL_FORMATS = (
    PixelFormat.Bgr8,
    PixelFormat.Bgr10,
    PixelFormat.Bgr12,
    PixelFormat.Bgr14,
    PixelFormat.Bgr16
)


BGRA_PIXEL_FORMATS = (
    PixelFormat.Bgra8,
    PixelFormat.Bgra10,
    PixelFormat.Bgra12,
    PixelFormat.Bgra14,
    PixelFormat.Bgra16
)


YUV_PIXEL_FORMATS = (
    PixelFormat.Yuv411,
    PixelFormat.Yuv422,
    PixelFormat.Yuv444
)


YCBCR_PIXEL_FORMATS = (
    PixelFormat.YCbCr411_8_CbYYCrYY,
    PixelFormat.YCbCr422_8_CbYCrY,
    PixelFormat.YCbCr8_CbYCr
)


COLOR_PIXEL_FORMATS = BAYER_PIXEL_FORMATS + RGB_PIXEL_FORMATS + RGBA_PIXEL_FORMATS + \
                      BGR_PIXEL_FORMATS + BGRA_PIXEL_FORMATS + YUV_PIXEL_FORMATS + \
                      YCBCR_PIXEL_FORMATS


OPENCV_PIXEL_FORMATS = (
    PixelFormat.Mono8,
    PixelFormat.Bgr8,
    PixelFormat.Bgra8,
    PixelFormat.Mono16,
    PixelFormat.Bgr16,
    PixelFormat.Bgra16
)


class AllocationMode(VmbIntEnum):
    """Enum specifying the supported frame allocation modes."""
    AnnounceFrame = 0          #: The buffer is allocated by vmbpy
    AllocAndAnnounceFrame = 1  #: The buffer is allocated by the Transport Layer


class Frame:
    """This class allows access to Frames acquired by a camera. The Frame is basically
    a buffer that wraps image data and some metadata.
    """
    def __init__(self,
                 buffer_size: int,
                 allocation_mode: AllocationMode,
                 buffer_alignment: int = 1):
        """Do not call directly. Create Frames via Camera methods instead."""
        self._allocation_mode = allocation_mode

        # Allocation is not necessary for the AllocAndAnnounce case. In that case the Transport
        # Layer will take care of buffer allocation. The self._buffer variable will be updated after
        # the frame is announced and memory has been allocated.
        if self._allocation_mode == AllocationMode.AnnounceFrame:
            if buffer_alignment > 1:
                # For aligned buffers not only must the starting point of the buffer fulfill the
                # requirement, but also the size of the buffer must fulfill it. This means the
                # buffer size allocated might be larger than what would be needed to hold the
                # transferred data
                buffer_size = _align_buffersize(buffer_size, alignment=buffer_alignment)
            self._buffer = _allocate_buffer(size=buffer_size, alignment=buffer_alignment)
        else:
            self._buffer = None
        self._frame: VmbFrame = VmbFrame()
        # Mark frame as invalid until it has been used at least once
        self._frame.receiveStatus = FrameStatus.Invalid

        # Setup underlaying Frame
        if self._allocation_mode == AllocationMode.AnnounceFrame:
            self._frame.buffer = ctypes.cast(self._buffer, ctypes.c_void_p)
            self._frame.bufferSize = sizeof(self._buffer)
        elif self._allocation_mode == AllocationMode.AllocAndAnnounceFrame:
            # Set buffer pointer to NULL and inform Transport Layer of size it should allocate
            self._frame.buffer = None
            self._frame.bufferSize = buffer_size
        self.__chunk_cb_exception: Optional[Exception] = None

    def __str__(self):
        msg = 'Frame(id={}, status={}, buffer={})'
        return msg.format(self._frame.frameID, str(FrameStatus(self._frame.receiveStatus)),
                          hex(self._frame.buffer))

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # VmbFrame contains Pointers and ctypes.Structure with Pointers can't be copied.
        # As a workaround VmbFrame contains a deepcopy-like Method performing deep copy of all
        # Attributes except PointerTypes. Those must be set manually after the copy operation.
        setattr(result, '_buffer', copy.deepcopy(self._buffer, memo))
        setattr(result, '_frame', self._frame.deepcopy_skip_ptr(memo))

        result._frame.buffer = ctypes.cast(result._buffer, ctypes.c_void_p)
        result._frame.bufferSize = sizeof(result._buffer)
        # calculate offset of original imageData pointer into original buffer
        if not self._frame.imageData:
            # imageData pointer is not set. We assume image data begins at the start of the buffer
            self._frame.imageData = ctypes.cast(ctypes.addressof(self._buffer),
                                                ctypes.POINTER(VmbUint8))
        image_data_offset = ctypes.addressof(self._frame.imageData.contents) - ctypes.addressof(self._buffer)  # noqa 501: E501
        # set new imageData pointer to same offset into new buffer
        result._frame.imageData = ctypes.cast(ctypes.byref(result._buffer, image_data_offset),
                                              ctypes.POINTER(VmbUint8))

        return result

    def _set_buffer(self, buffer: Union[ctypes.c_void_p, ctypes.Array]):
        """Set self._buffer to memory pointed to by passed buffer pointer

        Useful if frames were allocated with AllocationMode.AllocAndAnnounce
        """
        if isinstance(buffer, ctypes.Array) and buffer._type_ == ctypes.c_ubyte:
            if len(buffer) < self._frame.bufferSize:
                msg = 'The given buffer is {} bytes large but the needed bufferSize is {}'
                raise BufferError(msg.format(len(buffer), self._frame.bufferSize))
            self._buffer = buffer
        else:
            self._buffer = ctypes.cast(
                buffer,
                ctypes.POINTER(ctypes.c_ubyte * self._frame.bufferSize)
            ).contents

    def get_buffer(self) -> ctypes.Array:
        """Get internal buffer object containing image data and (if existent) chunk data."""
        return self._buffer

    def get_buffer_size(self) -> int:
        """Get byte size of internal buffer."""
        return self._frame.bufferSize

    def get_status(self) -> FrameStatus:
        """Returns current frame status."""
        return FrameStatus(self._frame.receiveStatus)

    def get_pixel_format(self) -> PixelFormat:
        """Get format of the acquired image data"""
        return PixelFormat(self._frame.pixelFormat)

    def get_height(self) -> Optional[int]:
        """Get image height in pixels.

        Returns:
            Image height in pixels if dimension data is provided by the camera. ``None`` if
            dimension data is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Dimension not in flags:
            return None

        return self._frame.height

    def get_width(self) -> Optional[int]:
        """Get image width in pixels.

        Returns:
            Image width in pixels if dimension data is provided by the camera. ``None`` if dimension
            data is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Dimension not in flags:
            return None

        return self._frame.width

    def get_offset_x(self) -> Optional[int]:
        """Get horizontal offset in pixels.

        Returns:
            Horizontal offset in pixel if offset data is provided by the camera. ``None`` if offset
            data is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Offset not in flags:
            return None

        return self._frame.offsetX

    def get_offset_y(self) -> Optional[int]:
        """Get vertical offset in pixels.

        Returns:
            Vertical offset in pixels if offset data is provided by the camera. ``None`` if offset
            data is not provided by the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Offset not in flags:
            return None

        return self._frame.offsetY

    def get_id(self) -> Optional[int]:
        """Get Frame ID.

        Returns:
            Frame ID if the id is provided by the camera. ``None`` if frame id is not provided by
            the camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.FrameID not in flags:
            return None

        return self._frame.frameID

    def get_timestamp(self) -> Optional[int]:
        """Get Frame timestamp.

        Returns:
            Timestamp if provided by the camera. ``None`` if timestamp is not provided by the
            camera.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.Timestamp not in flags:
            return None

        return self._frame.timestamp

    def get_payload_type(self) -> Optional[PayloadType]:
        """Returns the frame's payload type."""
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.PayloadType not in flags:
            return None

        return PayloadType(self._frame.payloadType)

    def contains_chunk_data(self) -> Optional[bool]:
        """Does the frame contain chunk data?

        Returns:
            ``True`` if frame contains chunk data, ``False`` if frame does not contain chunk data.
            ``None`` if this information is not provided by the underlying Transport Layer.
        """
        flags = decode_flags(VmbFrameFlags, self._frame.receiveFlags)

        if VmbFrameFlags.ChunkDataPresent not in flags:
            return None

        return bool(self._frame.chunkDataPresent)

    @TraceEnable()
    @RuntimeTypeCheckEnable()
    def access_chunk_data(self, callback: ChunkCallback) -> None:
        """Access chunk data for a frame.

        This function blocks until the user supplied callback has been executed. It may only be
        called inside a frame callback.

        Parameters:
            callback:
                A callback function that takes one argument. That argument will be a populated
                ``FeatureContainer`` instance. Only inside this callback is it possible to access
                the chunk features of the ``Frame`` instance.

        Raises:
            Any Exception:
                Any Exception raised in the user supplied callback

            VmbFrameError:
                If the frame does not contain any chunk data

            VmbChunkError:
                If some other error occurred during chunk handling
        """
        try:
            call_vmb_c('VmbChunkDataAccess',
                       byref(self._frame),
                       # assign user provided callback as closure to the lambda function. The lambda
                       # itself will be called from VmbC context and will provide access to the
                       # intended user provided callback in __chunk_cb_wrapper
                       CHUNK_CALLBACK_TYPE(lambda handle, _: self.__chunk_cb_wrapper(handle,
                                                                                     _,
                                                                                     callback)),
                       None)
        except VmbCError as e:
            # The chunk access function returned an error code other than `VmbError.Success`
            err = e.get_error_code()
            if err >= VmbError.Custom and self.__chunk_cb_exception:
                # Reset stored exception to None so we cannot mistake it as a new exception later on
                exc = self.__chunk_cb_exception
                self.__chunk_cb_exception = None
                raise exc
            elif err == VmbError.NoChunkData:
                raise VmbFrameError('No chunk data available') from e
            else:
                raise VmbChunkError('Error during chunk handling') from e

    def __chunk_cb_wrapper(self,
                           handle: VmbHandle,
                           _: ctypes.c_void_p,
                           user_callback: ChunkCallback) -> VmbError:
        """Internal helper Function for chunk access.

        Arguments:
            handle:
                VmbHandle that can be used to access Features via VmbC. Adding it to a
                ``FeatureContainer`` and attaching features will grant access as expected.
            _:
                A void pointer used in the C-API to allow users to pass context. Not used in VmbPy
            user_callback:
                The user provided function that should be called to access chunk features

        Returns:
            VmbError code that is interpreted by VmbC to check, if the chunk callback executed
            successfully. On successful execution this returns ``VmbError.Success``. If an exception
            occurred in the user supplied callback, a ``VmbError.Custom`` is returned. If an error
            code other than Success is returned here, this will in turn raise an Exception in
            ``Frame.access_chunk_data``. Exceptions raised by the user in their user_callback are
            stored and re-raised by ``Frame.access_chunk_data``
        """
        feats = FeatureContainer()
        feats._handle = handle
        try:
            feats._attach_feature_accessors()
            user_callback(feats)
        except Exception as e:
            msg = 'Caught Exception in chunk access function: '
            msg += 'Type: {}, '.format(type(e))
            msg += 'Value: {}, '.format(e)
            msg += 'raised by: {}'.format(user_callback)
            Log.get_instance().error(msg)
            # Store exception so it is accessible in `Frame.access_chunk_data`
            self.__chunk_cb_exception = e
            return VmbError.Custom
        finally:
            feats._remove_feature_accessors()

        return VmbError.Success

    @RuntimeTypeCheckEnable()
    def convert_pixel_format(self,
                             target_fmt: PixelFormat,
                             debayer_mode: Optional[Debayer] = None,
                             destination_buffer: Optional[memoryview] = None) -> 'Frame':
        """Return a converted version of the frame in the given format.

        This method always returns a new frame object and leaves the original instance unchanged.
        The returned frame object does not include the chunk data associated with the original
        instance. The original instance may for example be used for future frame transmissions.

        Note: This method allocates a new buffer for the returned image data leading to some runtime
        overhead. For performance reasons, it might be better to set the value of the camera's
        ``PixelFormat`` feature instead. In addition, a non-default debayer mode can be specified.

        Arguments:
            target_fmt:
                PixelFormat to convert to.
            debayer_mode:
                Non-default algorithm used to debayer images in Bayer Formats. If no mode is
                specified, default debayering mode of the image transform library is applied. If the
                current format is not a Bayer format, this parameter is silently ignored.
            destination_buffer:
                A buffer that the transformation result should be written to. The buffer must be
                large enough to hold the transformation result, writeable and be contiguous in
                memory. The recommended way to create a compatible buffer is to let
                ``convert_pixel_format`` perform a conversion *without* a ``destination_buffer`` and
                reuse the memory that was allocated for that transformation on future calls to
                ``convert_pixel_format``. See the `convert_pixel_format.py` example.

        Raises:
            TypeError:
                If parameters do not match their type hint. ValueError if the current format can't
                be converted into ``target_fmt``. Convertible Formats can be queried via
                ``get_convertible_formats()`` of ``PixelFormat``.
            AssertionError:
                If image width or height can't be determined.
            BufferError:
                If user supplied ``destination_buffer`` is too small, not writeable, or not
                contiguous in memory.
        """

        global BAYER_PIXEL_FORMATS

        # 1) Perform sanity checking
        fmt = self.get_pixel_format()

        if fmt != target_fmt and target_fmt not in fmt.get_convertible_formats():
            raise ValueError('Current PixelFormat can\'t be converted into given format.')

        # 2) Specify Transformation Input Image
        height = self._frame.height
        width = self._frame.width

        c_src_image = VmbImage()
        c_src_image.Size = sizeof(c_src_image)
        if self._frame.imageData:
            c_src_image.Data = ctypes.cast(self._frame.imageData, ctypes.c_void_p)
        else:
            c_src_image.Data = ctypes.cast(self._buffer, ctypes.c_void_p)

        call_vmb_image_transform('VmbSetImageInfoFromPixelFormat', fmt, width, height,
                                 byref(c_src_image))

        # 3) Specify Transformation Output Image
        c_dst_image = VmbImage()
        c_dst_image.Size = sizeof(c_dst_image)

        if fmt == target_fmt:
            # If the format does not change, ImageInfo will also remain the same. Just copy it to
            # prevent issues where formats that are not supported by ImageTransform library are
            # passed to this function
            c_dst_image.ImageInfo = c_src_image.ImageInfo
        else:
            layout, bits = PIXEL_FORMAT_TO_LAYOUT[VmbPixelFormat(target_fmt)]

            call_vmb_image_transform('VmbSetImageInfoFromInputImage', byref(c_src_image), layout,
                                     bits, byref(c_dst_image))

        # 4) Create output frame and carry over image metadata
        img_size = int(height * width * c_dst_image.ImageInfo.PixelInfo.BitsPerPixel / 8)
        if destination_buffer:
            if (destination_buffer.nbytes < img_size
                    or not destination_buffer.contiguous
                    or destination_buffer.readonly):
                msg = "User supplied buffer was not valid."
                if destination_buffer.nbytes < img_size:
                    msg += f" The size of the buffer does not match the image size. Buffer has " \
                           f"{destination_buffer.nbytes} bytes but {img_size} bytes are needed"
                raise BufferError(msg)
            # By using `AllocAndAnnounce` no buffer will be allocated by VmbPy. Instead the
            # user-supplied `destination_buffer` is used
            output_frame = Frame(buffer_size=img_size,
                                 allocation_mode=AllocationMode.AllocAndAnnounceFrame)
            output_frame._set_buffer((ctypes.c_ubyte * img_size).from_buffer(destination_buffer))
        else:
            # with `AnnounceFrame` the `Frame` class will allocate an appropriate buffer
            # automatically
            output_frame = Frame(buffer_size=img_size,
                                 allocation_mode=AllocationMode.AnnounceFrame)
        output_frame._frame = self._frame.deepcopy_skip_ptr({})
        c_dst_image.Data = ctypes.cast(output_frame._buffer, ctypes.c_void_p)

        # 5) Setup Debayering mode if given.
        transform_info = VmbTransformInfo()
        if debayer_mode and (fmt in BAYER_PIXEL_FORMATS):
            call_vmb_image_transform('VmbSetDebayerMode', VmbDebayerMode(debayer_mode),
                                     byref(transform_info))

        # 6) Perform Transformation
        if fmt == target_fmt:
            # No transformation is needed, simply copy over the data
            source = self._frame.imageData if self._frame.imageData else self._buffer
            ctypes.memmove(output_frame._buffer, source, img_size)
        else:
            call_vmb_image_transform('VmbImageTransform', byref(c_src_image), byref(c_dst_image),
                                     byref(transform_info), 1)

        # 7) Update frame metadata that changed due to transformation and buffer pointers that are
        #    not yet set correctly
        output_frame._frame.buffer = ctypes.cast(output_frame._buffer, ctypes.c_void_p)
        output_frame._frame.bufferSize = sizeof(output_frame._buffer)
        output_frame._frame.imageSize = img_size
        output_frame._frame.pixelFormat = target_fmt
        # For transformation results chunk data is no longer relevant so the imageData is the same
        # as the buffer start
        output_frame._frame.imageData = ctypes.cast(ctypes.byref(output_frame._buffer),
                                                    ctypes.POINTER(VmbUint8))

        return output_frame

    def as_numpy_ndarray(self) -> 'numpy.ndarray':
        """Construct ``numpy.ndarray`` view on VmbCFrame.

        Returns:
            ``numpy.ndarray`` on internal image buffer.

        Raises:
            ImportError:
                If numpy is not installed.
            VmbFrameError:
                If current PixelFormat can't be converted to a ``numpy.ndarray``.
        """
        if numpy is None:
            raise ImportError('\'Frame.as_numpy_ndarray()\' requires module \'numpy\'.')

        # Construct numpy overlay on underlying image buffer
        height = self._frame.height
        width = self._frame.width
        fmt = self._frame.pixelFormat

        c_image = VmbImage()
        c_image.Size = sizeof(c_image)

        call_vmb_image_transform('VmbSetImageInfoFromPixelFormat', fmt, width, height,
                                 byref(c_image))

        layout = PIXEL_FORMAT_TO_LAYOUT.get(fmt)

        if not layout:
            msg = 'Can\'t construct numpy.ndarray for Pixelformat {}. ' \
                  'Use \'frame.convert_pixel_format()\' to convert to a different Pixelformat.'
            raise VmbFrameError(msg.format(str(self.get_pixel_format())))

        bits_per_channel = layout[1]
        channels_per_pixel = c_image.ImageInfo.PixelInfo.BitsPerPixel // bits_per_channel
        image_size = width * height * channels_per_pixel * (bits_per_channel // 8)

        # ctypes arrays have the size encoded in their type. Define the full image data type here
        # for this frame
        array_type = ctypes.c_uint8 * image_size
        # cast the imageData pointer to a suitable type to create a numpy array from it
        if not self._frame.imageData:
            # imageData pointer is not set. We assume image data begins at the start of the buffer
            self._frame.imageData = ctypes.cast(ctypes.addressof(self._buffer),
                                                ctypes.POINTER(VmbUint8))
        image_data = ctypes.cast(self._frame.imageData, ctypes.POINTER(array_type))
        # Add self._buffer to dtype metadata. This makes sure, that a reference to that buffer is
        # kept while the numpy array still lives, preventing segfaults if the original VmbPy frame
        # goes out of scope and is garbage collected before the numpy array is accessed
        dt = numpy.dtype(numpy.uint8 if bits_per_channel == 8 else numpy.uint16,
                         metadata={'VmbPy_buffer': self._buffer})
        return numpy.ndarray(shape=(height, width, channels_per_pixel),
                             buffer=image_data.contents,
                             dtype=dt)

    def as_opencv_image(self) -> 'numpy.ndarray':
        """Construct OpenCV compatible view on VmbCFrame.

        Returns:
            OpenCV compatible ``numpy.ndarray``

        Raises:
            ImportError:
                If numpy is not installed.
            ValueError:
                If current pixel format is not compatible with opencv. Compatible formats are listed
                in ``OPENCV_PIXEL_FORMATS``.
        """
        global OPENCV_PIXEL_FORMATS

        if numpy is None:
            raise ImportError('\'Frame.as_opencv_image()\' requires module \'numpy\'.')

        fmt = self._frame.pixelFormat

        if fmt not in OPENCV_PIXEL_FORMATS:
            raise ValueError('Current Format \'{}\' is not in OPENCV_PIXEL_FORMATS'.format(
                             str(PixelFormat(self._frame.pixelFormat))))

        return self.as_numpy_ndarray()


@TraceEnable()
@RuntimeTypeCheckEnable()
def intersect_pixel_formats(fmts1: FormatTuple, fmts2: FormatTuple) -> FormatTuple:
    """Build intersection of two sets containing PixelFormat.

    Arguments:
        fmts1:
            PixelFormats to intersect with fmts2
        fmts2:
            PixelFormats to intersect with fmts1

    Returns:
        Set of PixelFormats that occur in ``fmts1`` and ``fmts2``

    Raises:
        TypeError:
            If parameters do not match their type hint.
    """
    return tuple(set(fmts1).intersection(set(fmts2)))


def _align_buffersize(size, alignment=1):
    offset = size % alignment
    offset_to_aligned = (alignment - offset) % alignment
    return size + offset_to_aligned


def _allocate_buffer(size, alignment=1):
    # Buffer can be at most (alignment -1) bytes out of alignment -> overallocate by that amount
    overallocated_size = size + (alignment - 1)
    overallocated_memory = (ctypes.c_ubyte * overallocated_size)()

    # how far off from desired alignment does the overallocated_memory start
    offset = ctypes.addressof(overallocated_memory) % alignment

    # how far into overallocated_memory can the first aligned address be found
    offset_to_aligned = (alignment - offset) % alignment

    return (ctypes.c_ubyte * size).from_buffer(overallocated_memory, offset_to_aligned)
