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
    def enable(self):
        self.enabled = True
        print(f'debugging.enabled: {self.enabled}')
    def disable(self):
        self.enabled = False
        print(f'debugging.enabled: {self.enabled}')
# debugger Instance
debugging = debugging()
def debug(message="", obj=None):
    if debugging.enabled:
        if obj is not None:
            obj = pformat(obj)
        else:
            obj = ""
        print(f'%s' % message, end="")



##### Base Models all Classes originate from #################

class O365BaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed=True

_parameterOptions = {}
class RestParameter(Enum):  
    def __init_subclass__(cls, ParamName=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if ParamName == None:
            ParamName = cls.__name__
        _parameterOptions[ParamName] = \
                [ option for option in dir(cls) if option[0] != '_' ]

##### Enumerations ###########################################

class URI:
    def version(self): 
        return 'https://endpoints.office.com/version'

    def endpoints(self, Instance):
        return f'https://endpoints.office.com/endpoints/{Instance}'

    def changes(self, serviceArea, version):
        return f'https://endpoints.office.com/changes/{serviceArea}/{version}'
# singleton
URI = URI()


class InstanceParam(str, RestParameter):
    """ Office Instances by Physical Segmentation boundary
    """
    Worldwide    = 'Worldwide'
    USGovDod     = 'USGovDoD'
    USGovGCCHigh = 'USGovGCCHigh'
    China        = 'China'
    Germany      = 'Germany'

class ServiceAreaParam(str, RestParameter): 
    """ ServiceArea options that can be filtered for in requests 
    """
    Common       = 'Common'
    Exchange     = 'Exchange'
    SharePoint   = 'SharePoint'
    Skype        = 'Skype'

    __or__= lambda left, right: ','.join((left.value, right.value))

class DispositionParam(str, RestParameter):
    """ trigger which evoked version increment.
    """
    change       = 'change'
    add          = 'add'
    remove       = 'remove'

class CategoryParam(str, RestParameter):
    """ reason for update resulting in version increment
    """
    Optimize     = 'Optimize'
    Allow        = 'Allow'
    Default      = 'Default'

class FormatParam(str, RestParameter):
    """ Expected format of response.
    """
    JSON         = 'JSON'
    CSV          = 'CSV'

class ImpactParam(str, RestParameter):
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
          Instance version
"""
class InstanceVersion(BaseModel):
    """ 
        Version metadata per Instance.

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


    # reusable validator to cast 10-digit version str into Version Instance.
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

        serviceArea  -> <ServiceAreaParam>
        urls         -> ( str, ... )
        tcpPorts     -> str (comma separated list of ports and port-ranges)
        udpPorts     -> str (comma separated list of ports and port-ranges_)
        category     -> <CategoryParam>
        expressRoute -> bool
        required     -> bool
        notes        -> str

    """
    serviceArea:            ServiceAreaParam
    urls:                   List[str]
    tcpPorts:               str # conint(ge=0, lt=65535)
    udpPorts:               str # conint(ge=0, lt=65535)
    category:               CategoryParam
    expressRoute:           bool
    required:               bool
    notes:                  Optional[str]



##### Response Models #######################################

class VersionModel(O365BaseModel):
    """
        describes Instance version(s) when a change occured

    ATTRIBUTES
        
        Instance: <InstanceParam>
        latest:   <InstanceVersion>
        versions: ( <InstanceVersion, ... )
    """
    Instance: InstanceParam
    latest:   Union[InstanceVersion, str]
    versions: Optional[List[Union[InstanceVersion, str]]]


class EndpointsModel(ServiceAtomModel):
    """
        describes an endpoint

    ATTRIBUTES

        id -> int
        serviceArea            -> <ServiceAreaParam>
        serviceAreaDisplayName -> str
        urls                   -> ( str, ... )
        ips                    -> ( str, ... )
        tcpPorts               -> str (comma separated list of ports and port-ranges)
        udpPorts               -> str (comma separated list of ports and port-ranges)
        category               -> <CategoryParam>
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
        disposition            -> <DispositionParam>
        impact                 -> <ImpactParam>
        version                -> InstanceVersion
        previous               -> <ServiceAtomModel>
        current                -> <ServiecAtomModel>
        add                    -> <ChangeAtomModel>
        remove                 -> <ChangeAtomModel>


    """
    id:                     int
    endpointSetId:          int
    disposition:            DispositionParam
    impact:                 ImpactParam
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
        into Instances of `Model`.

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
        InstanceList = []
        length = 0
        for entry in json:
            InstanceList.append( Model.parse_obj(entry) )
            length += 1
        return length, tuple(InstanceList)
    debug("o365ipAddr_json.jsonResponse:\n%s\n" % pformat(jsonResponse))
    return 1, Model.parse_obj(json)

def o365ipAddr_get(
        Model, 
        URI:    str, 
        Format: FormatParam = FormatParam.JSON,
        **options):
    params = {} 
    params['ClientRequestId'] = str(uuid4())
    params['Format']          = Format.value
    for key in options.keys():
        if options[key] is not None:
            params[key] = options[key]
    debug("o365ipAddr_get: GET %s?%s HTTP/1.1\n" % (URI, uu(params)))
    response = requests.get(URI, params=params)
    if response.ok:
        if Format == FormatParam.JSON:
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
        AllVersions:   bool             = False,
        Instance:      InstanceParam    = InstanceParam.Worldwide,
        Format:        FormatParam      = FormatParam.JSON):
    """
        Retrieves Instance version information for office 365 connectivity
        information, allowing use in policy management and context-based
        authorization control systems, such as firewalls, proxies, etc.) 

    ARGUMENTS

        AllVersions: <bool>
              True: retrieves the versions field which contains a list of
              all versions

              False: (default) retrieves the current versions only.

        Instance: <InstanceParam>
              Worldwide: Service location information pertianing to worldwide
              hosted office Instances with the exception of the following
              Instances.

              USGovDod: Service location information pertaining to Department
              of defense segmented office Instances.

              USGovGCCHigh: Service location inforamtion pertaining to
              Government Comunity Cloud - High Security Instances.

              China: Service location information isolated to China secured
              intra-country datacenters. Operated by 21Vianet.
              Instances.

              Germany: Service location information isolated to German secured
              intra-country datacenters.

        Format: <FormatParam>
              JSON returns JSON data, and CSV returns comma separated values
              as string data.


    RETURNS

       ( length, ( <VersionModel object at 0x...>, ...) )   # if list of Versions
       ( 1,        <VersionModel object at 0x...> )         # single Version
       ( None,      str )                                   # TextData (CSV)

    """
    params = {
        'Format':          Format,
        'AllVersions':     AllVersions,
        'Instance':        Instance
    }
    return o365ipAddr_get(VersionModel, URI.version(), **params)


def getEndpoints(
        Instance:      InstanceParam    = InstanceParam.Worldwide,
        Format:        FormatParam      = FormatParam.JSON,
        ServiceAreas:  ServiceAreaParam = None,
        TenantName:    str             = None,
        NoIPv6:        bool            = False):
    """
        Retrieves versioned lists of location information (IP Addresses, IP
        Prefixes, Address Ranges, URLs, and UDP/DCP Ports) as well as
        supporting metadata to derive context-based access control policy
        from in Firewalls, Proxies, etc.

    ARGUMENTS

        ServiceAreas: ServiceAreaParam
    """
    params = {
        'Format':          Format,
        'ServiceAreas':    ServiceAreas,
        'TenantName':      TenantName,
        'NoIPv6':          NoIPv6,
    }
    return o365ipAddr_get(EndpointsModel, URI.endpoints(Instance.value), **params)


def getChanges(
        Instance:      InstanceParam    = InstanceParam.Worldwide,
        Version:       InstanceVersion  = '0000000000',
        Format:        FormatParam      = FormatParam.JSON):
    """ 
        Retrieves changes from o365.
    """
    return o365ipAddr_get(ChangesModel, URI.changes(Instance.value, str(Version)), Format=Format)

