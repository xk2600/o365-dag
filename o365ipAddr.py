#!/usr/bin/env python3


import requests
import requests_cache
requests_cache.install_cache('o365', backend='memory')
from urllib.parse import urlencode as uu

from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic import create_model, parse_obj_as
from pydantic import validator, root_validator
from pydantic import conint

from typing import List, Dict, Union, Optional, Any, ClassVar
from enum import Enum
from datetime import date

import re
from pprint import PrettyPrinter
pformat = PrettyPrinter(indent=2, compact=False).pformat


# conditional debugger
class debugging:
    enabled: str = False
    @property
    def enable(self):
        print(f'debugging: {enable}')
        self.enabled = True
    def disable():
        print(f'debugging: {enable}')
        self.disabled = False
# debugger instance
debugging = debugging()
def debug(message="", obj=None):
    if debugging.enabled:
        if obj is not None:
            obj = pformat(obj)
        else:
            obj = ""
        print(f'%s' % message, end="")



##### Pydantic BaseModel and Configuration ###################

class O365BaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed=True



##### Enumerations ###########################################

class URI:
    version: str = 'https://endpoints.office.com/version'

    @property
    def endpoints(self, instance):
        return f'https://endpoints.office.com/endpoints/{instance}'

    @property
    def changes(self, serviceArea, version):
        return f'https://endpoints.office.com/changes/{serviceArea}/{version}'
# singleton
URI = URI()


class InstanceEnum(str, Enum):
    """ Office Instances by Physical Segmentation boundary
    """
    Worldwide    = 'Worldwide'
    USGovDod     = 'USGovDoD'
    USGovGCCHigh = 'USGovGCCHigh'
    China        = 'China'
    Germany      = 'Germany'

class ServiceAreaEnum(str, Enum): 
    """ ServiceArea options that can be filtered for in requests 
    """
    Common       = 'Common'
    Exchange     = 'Exchange'
    SharePoint   = 'SharePoint'
    Skype        = 'Skype'

    __or__= lambda left, right: ','.join((left.value, right.value))

class DispositionEnum(str, Enum):
    """ trigger which evoked version increment.
    """
    change       = 'change'
    add          = 'add'
    remove       = 'remove'

class CategoryEnum(str, Enum):
    """ reason for update resulting in version increment
    """
    Optimize     = 'Optimize'
    Allow        = 'Allow'
    Default      = 'Default'

class FormatEnum(str, Enum):
    """ Expected format of response.
    """
    JSON         = 'JSON'
    CSV          = 'CSV'

class ImpactEnum(str, Enum):
    """ Impact description as a result of not updating current policy with
        changes notated in this version.
    """
    AddedIp                 = 'AddedIp'
    AddedUrl                = 'AddedUrl'
    AddedIpAndUrl           = 'AddedIpAndUrl'
    RemovedIpOrUrl          = 'RemovedIpOrUrl'
    ChangedIsExpressRoute   = 'ChangedIsExpressRoute'
    MovedIpOrUrl            = 'MovedIpOrUrl'
    RemovedDuplicateIpOrUrl = 'RemovedDuplicateIpOrUrl'
    OtherNonPriorityChanges = 'OtherNonPriorityChanges'




##### Supporting Models ######################################

""" Version --
          instance version
"""
class InstanceVersion(BaseModel):
    """ 
        Version metadata per instance.

    ATTRIBUTES

        date -> datetime.date

        intraday: int
              intraday increment updates when multiple versions must exist
              due to multiple changes in a single day.

        current -> bool
              True: this is the most current version.

        value -> str
              str formatted appropriately for data-exchange with o365 API
    """
    date:     Optional[date]
    intraday: int
    
    re:       ClassVar[Any]  = re.compile(
        r'('
        r'([0-9][0-9][0-9][0-9])' # YYYY (Year)
        r'([0][1-9]|[1][0-2])'    # MM (Month)
        r'([0-2][0-9]|[3][01])'   # DD (Day)
        r'([0-9][0-9])'           # NN (intraday incrementing index)
        r'|00000000)' )           # permit all zeros.

    """ regex --
              re compiled version processor
    """
    @property
    def regex(self):
        return self.re
    """ Version.current --
              returns whether this version is the current version.
    """
    @property
    def current(self):
        return isinstance(self.date, None)

    def __str__(self):
        return ('%02s%02s%02s%02s' % (
                self.date.year, 
                self.date.month, 
                self.date.day, 
                self.intraday)
            ).replace(' ', '0')

    @property
    def value(self):
        return str(self)


    # reusable validator to cast 10-digit version str into Version instance.
    @root_validator(pre=True)
    def validate_version(cls, v):
        if not isinstance(v, str or InstanceVersion):
            raise TypeError('version should be of type str or InstanceVersion')
        if isinstance(v, InstanceVersion):
            return v
        m = InstanceVersion.re.fullmatch(v)
        if not m:
            raise ValueError(f'invalid version number "{v}": should be formatted "YYYYMMDDNN" or "0000000000".')
        # validated... return None if date == 0, or return cls(date, intraday)
        if int(v) == 0:
            return cls( date=None, intraday=None )
        else:
            #  xlate groups[0:2] to 'YYYY-MM-DD'     cast group(4) to int
            return cls(date='-'.join(m.groups[0:3]), intraday=int(m.group(4)))



    

class ChangeAtomModel(O365BaseModel):
    """ 
        represents the components of a single change

    ATTRIBUTES

        effectiveDate -> datetime.date
              when this change will take effect

        ips -> (str, ...)
              IP Addresses, IP Prefixes, IP Address Ranges

        urls -> (str, ...)
              Fully Qualified domain names
    """
    effectiveDate:          date
    ips:                    Optional[List[str]]
    urls:                   Optional[List[str]]
    
    @validator('effectiveDate')
    def _validate_effectiveDate(cls, v):
        assert len(v) == 8
        return date(v[0:4], v[4:6], v[6:8])

class ServiceAtomModel(O365BaseModel):
    """
        describes current active endpoints in o365.

    ATTRIBUTES

        serviceArea  -> <ServiceAreaEnum>
        urls         -> ( str, ... )
        tcpPorts     -> str (comma separated list of ports and port-ranges)
        udpPorts     -> str (comma separated list of ports and port-ranges_)
        category     -> <CategoryEnum>
        expressRoute -> bool
        required     -> bool
        notes        -> str

    """
    serviceArea:            ServiceAreaEnum
    urls:                   List[str]
    tcpPorts:               str # conint(ge=0, lt=65535)
    udpPorts:               str # conint(ge=0, lt=65535)
    category:               CategoryEnum
    expressRoute:           bool
    required:               bool
    notes:                  Optional[str]



##### Response Models #######################################

class VersionModel(O365BaseModel):
    """
        describes instance version(s) when a change occured

    ATTRIBUTES
        
        instance: <InstanceEnum>
        latest:   <InstanceVersion>
        versions: ( <InstanceVersion, ... )
    """
    instance: InstanceEnum
    latest:   Union[InstanceVersion, str]
    versions: Optional[List[Union[InstanceVersion, str]]]


class EndpointsModel(ServiceAtomModel):
    """
        describes an endpoint

    ATTRIBUTES

        id -> int
        serviceArea            -> <ServiceAreaEnum>
        serviceAreaDisplayName -> str
        urls                   -> ( str, ... )
        ips                    -> ( str, ... )
        tcpPorts               -> str (comma separated list of ports and port-ranges)
        udpPorts               -> str (comma separated list of ports and port-ranges)
        category               -> <CategoryEnum>
        expressRoute           -> bool
        required               -> bool
        notes                  -> str


    """
    id:                     int
    serviceAreaDisplayName: Optional[str]
    ips:                    Optional[List[str]]

class ChangesModel(O365BaseModel):
    """
        describes moves, adds, and change events.

    ATTRIBUTE
    
        id                     -> int
        endpointSetId          -> int
        disposition            -> <DispositionEnum>
        impact                 -> <ImpactEnum>
        version                -> InstanceVersion
        previous               -> <ServiceAtomModel>
        current                -> <ServiecAtomModel>
        add                    -> <ChangeAtomModel>
        remove                 -> <ChangeAtomModel>


    """
    id:                     int
    endpointSetId:          int
    disposition:            DispositionEnum
    impact:                 ImpactEnum
    version:                Union[InstanceVersion, str]
    previous:               ServiceAtomModel
    current:                ServiceAtomModel
    add:                    ChangeAtomModel
    remove:                 ChangeAtomModel



##### Implementation ########################################

def o365ipAddr_json(Model, json):
    """ 
        Handles obscure scenarious where the json root contains a list instead 
        of a dictionary. (come on Microsoft, really? https://json-schema.org/)
        Effectively, this shim's the Model.parse_obj(...) behavior already built
        into the Pydantic package. I'm sure there is a Pydantic way to solve this
        problem, however, I couldn't readily figure it out using __root__
        validators and so this is the duct tape that shall function in it's place.

        if `json` is a list of `Model`s, iterate over them as we parse the json
        into instances of `Model`.

    ARGUMENTS

        Model
              Pydantic Model representing data in `json`

        json  
              `dict` representation (or list of `dict`s) of json
              response from server.

    RETURNS   

       ( length, ( <Model object at 0x...>, ...) )   # if list of Models
       ( 1,        <Model object at 0x...>       )   # if a single Model
    """
    debug('o365ipAddr_json:\n%s\n' % (pformat(json)))
    if isinstance(json, list):
        instanceList = []
        length = 0
        for entry in json:
            instanceList.append( Model.parse_obj(entry) )
            length += 1
        return length, tuple(instanceList)
    debug("o365ipAddr_json.jsonResponse:\n%s\n" % pformat(jsonResponse))
    return 1, Model.parse_obj(json)

def o365ipAddr_get(
        Model, 
        URI:    str, 
        Format: FormatEnum = FormatEnum.JSON,
        **params):
    params['ClientRequestId'] = str(uuid4())
    params['Format']          = Format.value
    debug("o365ipAddr_get: GET %s?%s HTTP/1.1\n" % (URI, uu(params)))
    response = requests.get(URI, params=params)
    if response.ok:
        if Format == FormatEnum.JSON:
            # JSON Response (hopefully)... 
            ModelCount, Models = o365ipAddr_json(Model, response.json())
        else:
            # Asked for other arbitrary data (CSV)
            debug('o365ipAddr_get.text: %s\n' % (response.text))
            ModelCount, TextData = None, response.text
        debug("o365ipAddr_get.return(ModelCount, Models) -> %s,\n%s\n\n" 
                % (ModelCount, pformat(Models)))
        return ModelCount, Models
    else:
        response.raise_for_status()

def getVersion(
        AllVersions:   bool            = False,
        Instance:      InstanceEnum    = InstanceEnum.Worldwide,
        Format:        FormatEnum      = FormatEnum.JSON):
    """
        Retrieves instance version information for office 365 connectivity
        information, allowing use in policy management and context-based
        authorization control systems, such as firewalls, proxies, etc.) 

    ARGUMENTS

        Format: <FormatEnum>
              JSON returns JSON data, and CSV returns comma separated values
              as string data.

        AllVersions: <bool>
              True: retrieves the versions field which contains a list of
              all versions

              False: (default) retrieves the current versions only.

        Instance: <InstanceEnum>
              Worldwide: Service location information pertianing to worldwide
              hosted office instances with the exception of the following
              instances.

              USGovDod: Service location information pertaining to Department
              of defense segmented office instances.

              USGovGCCHigh: Service location inforamtion pertaining to
              Government Comunity Cloud - High Security Instances.

              China: Service location information isolated to China secured
              intra-country datacenters. Operated by 21Vianet.
              Instances.

              Germany: Service location information isolated to German secured
              intra-country datacenters.

    RETURNS

       ( length, ( <VersionModel object at 0x...>, ...) )   # if list of Versions
       ( 1,        <VersionModel object at 0x...> )         # single Version
       ( None,      str )                                   # TextData (CSV)

    """
    params = {
        'Format':          Format,
        'AllVersions':     AllVersions,
        'Instance':        Instance.value
    }
    return o365ipAddr_get(VersionModel, URI.version, **params)


def getEndpoints(
        Instance:      InstanceEnum    = InstanceEnum.Worldwide,
        Format:        FormatEnum      = FormatEnum.JSON,
        ServiceAreas:  ServiceAreaEnum = None,
        TenantName:    str             = None,
        NoIPv6:        bool            = False):
    """
        Retrieves versioned lists of location information (IP Addresses, IP
        Prefixes, Address Ranges, URLs, and UDP/DCP Ports) as well as
        supporting metadata to derive context-based access control policy
        from in Firewalls, Proxies, etc.

    ARGUMENTS

        ServiceAreas: ServiceAreaEnum
    """
    params = {
        'Format':          Format.value,
        'ServiceAreas':    ServiceAreavalue,
        'TenantName':      TenantName,
        'NoIPv6':          NoIPv6,
    }
    return o365ipAddr_get(EndpointsModel, URI.endpoints(Instance), **params)


def getChanges(
        Instance:      InstanceEnum    = InstanceEnum.Worldwide,
        Version:       InstanceVersion = '0000000000',
        Format:        FormatEnum      = FormatEnum.JSON):
    """ 
        Retrieves changes from o365.
    """
    return o365ipAddr_get(ChangesModel, URI.changes(Instance.value, str(Version)), Format=Format)

