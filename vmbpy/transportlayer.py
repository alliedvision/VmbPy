import enum
from ctypes import byref, sizeof
from typing import List, Tuple

from .c_binding import VmbTransportLayer, VmbTransportLayerInfo, VmbUint32, VmbHandle, call_vmb_c, \
                       decode_cstr
from .feature import discover_features, FeaturesTuple
# from .interface import InterfacesTuple
from . import vmbsystem
from .shared import attach_feature_accessors
from .util import TraceEnable


# Forward declarations
TransportLayersTuple = Tuple['TransportLayer', ...]
TransportLayerList = List['TransportLayer']


class TransportLayerType(enum.IntEnum):
    """Enum specifying all interface types.

    Enum values:
        Unknown  - Interface is not known to this version of the API
        GEV      - GigE Vision
        CL       - Camera Link
        IIDC     - IIDC 1394
        UVC      - USB video class
        CXP      - CoaXPress
        CLHS     - Camera Link HS
        U3V      - USB3 Vision Standard
        Ethernet - Generic Ethernet
        PCI      - PCI / PCIe
        Custom   - Non standard
        Mixed    - Mixed (transport layer only)
    """
    Unknown = VmbTransportLayer.Unknown
    GEV = VmbTransportLayer.GEV
    CL = VmbTransportLayer.CL
    IIDC = VmbTransportLayer.IIDC
    UVC = VmbTransportLayer.UVC
    CXP = VmbTransportLayer.CXP
    CLHS = VmbTransportLayer.CLHS
    U3V = VmbTransportLayer.U3V
    Ethernet = VmbTransportLayer.Ethernet
    PCI = VmbTransportLayer.PCI
    Custom = VmbTransportLayer.Custom
    Mixed = VmbTransportLayer.Mixed


class TransportLayer:
    def __init__(self, info: VmbTransportLayerInfo):
        """Do not call directly. Access Transport Layers via vmbpy.VmbSystem instead."""
        self.__info: VmbTransportLayerInfo = info
        self.__handle: VmbHandle = self.__info.transportLayerHandle
        # TODO: Should this happen in an _open method like it does in Interface?
        # Probably depends on decision regarding __enter__ and __exit__ requirement
        self.__feats: FeaturesTuple = discover_features(self.__handle)
        attach_feature_accessors(self, self.__feats)

    # __enter__ and __exit__ required or does VmbC handle opening these for us?

    def __str__(self):
        return 'TransportLayer(id={})'.format(self.get_id())

    def __repr__(self) -> str:
        rep = 'TransportLayer'
        rep += '(__handle=' + repr(self.__handle)
        rep += ',__info=' + repr(self.__info)
        rep += ')'
        return rep

    # TODO: how to handle typing? importing InterfacesTuple from .interface leads to circular imports and errors
    def get_interfaces(self):
        with vmbsystem.VmbSystem.get_instance() as vmb:
            return vmb.get_interfaces_by_tl(self)

    # TODO: Also a looming typing issue here?
    def get_cameras(self):
        with vmbsystem.VmbSystem.get_instance() as vmb:
            return vmb.get_cameras_by_tl(self)

    def get_id(self):
        return decode_cstr(self.__info.transportLayerIdString)

    def get_name(self):
        return decode_cstr(self.__info.transportLayerName)

    def get_model_name(self):
        return decode_cstr(self.__info.transportLayerModelName)

    def get_vendor(self):
        return decode_cstr(self.__info.transportLayerVendor)

    def get_version(self):
        return decode_cstr(self.__info.transportLayerVersion)

    def get_path(self):
        return decode_cstr(self.__info.transportLayerPath)

    def get_type(self):
        return TransportLayerType(self.__info.transportLayerType)

    def _get_handle(self):
        return self.__handle


@TraceEnable()
def discover_transport_layers() -> TransportLayerList:
    """Do not call directly. Access Transport Layers via vmbpy.VmbSystem instead."""
    result = []
    transport_layers_count = VmbUint32(0)

    call_vmb_c('VmbTransportLayersList',
               None,
               0,
               byref(transport_layers_count),
               sizeof(VmbTransportLayerInfo))

    if transport_layers_count:
        transport_layers_found = VmbUint32(0)
        transport_layer_infos = (VmbTransportLayerInfo * transport_layers_count.value)()

        call_vmb_c('VmbTransportLayersList',
                   transport_layer_infos,
                   transport_layers_count,
                   byref(transport_layers_found),
                   sizeof(VmbTransportLayerInfo))
        for info in transport_layer_infos[:transport_layers_found.value]:
            result.append(TransportLayer(info))

    return result
