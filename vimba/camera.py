"""Camera access.

This module allows access to a detected camera.

(C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

<Insert license here>
"""
import enum
from typing import Tuple, cast
from vimba.c_binding import call_vimba_c_func, byref, sizeof, decode_cstr, decode_flags
from vimba.c_binding import VmbCameraInfo, VmbHandle, VmbUint32, G_VIMBA_HANDLE, VmbAccessMode, \
                            VimbaCError, VmbError
from vimba.feature import discover_features, discover_feature, filter_features_by_name, \
                          filter_features_by_type, filter_affected_features, \
                          filter_selected_features, FeatureTypes, FeaturesTuple
from vimba.util import RuntimeTypeCheckEnable
from vimba.error import VimbaSystemError


__all__ = [
    'AccessMode',
    'Camera',
    'CamerasTuple',
    'discover_cameras'
]


class AccessMode(enum.IntEnum):
    """Enum specifying all available access modes for camera access.

    Enum values:
        None_  - No access
        Full   - Read and write access
        Read   - Read-only access
        Config - Configuration access (GeV)
        Lite   - Read and write access without feature access (only addresses)
    """
    None_ = VmbAccessMode.None_
    Full = VmbAccessMode.Full
    Read = VmbAccessMode.Read
    Config = VmbAccessMode.Config
    Lite = VmbAccessMode.Lite


class Camera:
    """This class allows access a Camera detected by the Vimba System.
    Camera is meant be used in conjunction with the "with" - Statement. On entering a context
    all Camera features are detected and can be accessed within the context.
    Basic Camera properties like Name and Model can be access outside of the context.
    """

    def __init__(self, info: VmbCameraInfo, access_mode: AccessMode):
        """Do not call directly. Access Cameras via vimba.System instead."""
        self.__handle: VmbHandle = VmbHandle(0)
        self.__info: VmbCameraInfo = info
        self.__access_mode: AccessMode = access_mode
        self.__feats: FeaturesTuple = ()
        self.__context_cnt: int = 0

    def __enter__(self):
        if not self.__context_cnt:
            self._open()

        self.__context_cnt += 1
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__context_cnt -= 1

        if not self.__context_cnt:
            self._close()

    def __str__(self):
        return 'Camera(id={})'.format(self.get_id())

    def __repr__(self):
        rep = 'Camera'
        rep += '(__handle=' + repr(self.__handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    @RuntimeTypeCheckEnable()
    def set_access_mode(self, access_mode: AccessMode):
        """Set camera access mode.

        Arguments:
            mode - AccessMode used on accessing a Camera. This method
                must be used before entering the Context with the 'with' statement.

        Raises:
           TypeError if 'mode' is not of type AccessMode.
        """
        self.__access_mode = access_mode

    def get_access_mode(self) -> AccessMode:
        """Get camera access mode

        Returns:
            Currently configured camera access mode
        """
        return self.__access_mode

    def get_id(self) -> str:
        """Get Camera Id, e.g. DEV_1AB22C00041B"""
        return decode_cstr(self.__info.cameraIdString)

    def get_name(self) -> str:
        """Get Camera Name, e.g. Allied Vision 1800 U-500m"""
        return decode_cstr(self.__info.cameraName)

    def get_model(self) -> str:
        """Get Camera Model, e.g. 1800 U-500m"""
        return decode_cstr(self.__info.modelName)

    def get_serial(self) -> str:
        """Get Camera Serial, e.g. 000T7"""
        return decode_cstr(self.__info.serialString)

    def get_permitted_access_modes(self) -> Tuple[AccessMode, ...]:
        """Get a set of all access modes, the camera can be accessed with."""
        return decode_flags(AccessMode, self.__info.permittedAccess)

    def get_interface_id(self) -> str:
        """Get ID of the Interface this camera is connected to, e.g. VimbaUSBInterface_0x0"""
        return decode_cstr(self.__info.interfaceIdString)

    def get_all_features(self) -> FeaturesTuple:
        """Get access to all discovered features of this camera:

        Returns:
            A set of all currently detected features. Returns an empty set then called
            outside of 'with' - statement.
        """
        return self.__feats

    @RuntimeTypeCheckEnable()
    def get_features_affected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features affected by a specific camera feature.

        Arguments:
            feat - Feature used find features that are affected by 'feat'.

        Returns:
            A set of features affected by changes on 'feat'. Can be an empty set if 'feat'
            does not affect any features.

        Raises:
            TypeError if 'feat' is not of any feature type.
            VimbaFeatureError if 'feat' is not a feature of this camera.
        """
        return filter_affected_features(self.__feats, feat)

    @RuntimeTypeCheckEnable()
    def get_features_selected_by(self, feat: FeatureTypes) -> FeaturesTuple:
        """Get all features selected by a specific camera feature.

        Arguments:
            feat - Feature used find features that are selected by 'feat'.

        Returns:
            A set of features selected by changes on 'feat'. Can be an empty set if 'feat'
            does not affect any features.

        Raises:
            TypeError if 'feat' is not of any feature type.
            VimbaFeatureError if 'feat' is not a feature of this camera.
        """
        return filter_selected_features(self.__feats, feat)

    #@RuntimeTypeCheckEnable()
    def get_features_by_type(self, feat_type: FeatureTypes) -> FeaturesTuple:
        """Get all camera features of a specific feature type.

        Valid FeatureTypes are: IntFeature, FloatFeature, StringFeature, BoolFeature,
        EnumFeature, CommandFeature, RawFeature

        Arguments:
            feat_type - FeatureType used find features of that type.

        Returns:
            A set of features of type 'feat_type'. Can be an empty set if there is
            no camera feature with the given type available.

        Raises:
            TypeError if 'feat_type' is not of any feature Type.
        """
        return filter_features_by_type(self.__feats, feat_type)

    @RuntimeTypeCheckEnable()
    def get_feature_by_name(self, feat_name: str) -> FeatureTypes:
        """Get a camera feature by its name.

        Arguments:
            feat_name - Name used to find a feature.

        Returns:
            Feature with the associated name.

        Raises:
            TypeError if 'feat_name' is not of type 'str'.
            VimbaFeatureError if no feature is associated with 'feat_name'.
        """
        return filter_features_by_name(self.__feats, feat_name)

    def _open(self):
        exc = None

        try:
            call_vimba_c_func('VmbCameraOpen', self.__info.cameraIdString, self.__access_mode,
                              byref(self.__handle))

        except VimbaCError as e:
            exc = cast(VimbaSystemError, e)
            err = e.get_error_code()

            # In theory InvalidAccess should be thrown on using a non permitted access mode.
            # In reality VmbError.NotImplemented_ is returned.
            if err == VmbError.InvalidAccess or err == VmbError.NotImplemented_:
                msg = 'Accessed Camera \'{}\' with invalid Mode \'{}\'. Valid modes are: {}'
                msg = msg.format(self.get_id(), str(self.__access_mode),
                                 self.get_permitted_access_modes())

                exc = VimbaSystemError(msg)

        if exc:
            raise exc

        self.__feats = discover_features(self.__handle)

    def _close(self):
        for feat in self.__feats:
            feat.unregister_all_change_handlers()

        self.__feats = ()

        call_vimba_c_func('VmbCameraClose', self.__handle)

        self.__handle = VmbHandle(0)


def _setup_network_discovery():
    if discover_feature(G_VIMBA_HANDLE, 'GeVTLIsPresent').get():
        discover_feature(G_VIMBA_HANDLE, 'GeVDiscoveryAllDuration').set(250)
        discover_feature(G_VIMBA_HANDLE, 'GeVDiscoveryAllOnce').run()


CamerasTuple = Tuple[Camera, ...]


def discover_cameras(access_mode: AccessMode, network_discovery: bool) -> CamerasTuple:
    """Do not call directly. Access Cameras via vimba.System instead."""

    if network_discovery:
        _setup_network_discovery()

    result = []
    cams_count = VmbUint32(0)

    call_vimba_c_func('VmbCamerasList', None, 0, byref(cams_count), 0)

    if cams_count:
        cams_found = VmbUint32(0)
        cams_infos = (VmbCameraInfo * cams_count.value)()

        call_vimba_c_func('VmbCamerasList', cams_infos, cams_count, byref(cams_found),
                          sizeof(VmbCameraInfo))

        for info in cams_infos[:cams_found.value]:
            result.append(Camera(info, access_mode))

    return tuple(result)
