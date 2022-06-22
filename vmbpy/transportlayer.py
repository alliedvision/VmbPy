import enum

from .c_binding import VmbTransportLayer

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
