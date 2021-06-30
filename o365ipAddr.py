#!/usr/bin/env python3

import requests
from uuid import uuid4
from pydantic import BaseModel, Field
from pydantic import create_model, parse_obj_as
from pydantic import validator, root_validator

class URI:
    version:   str = 'https://endpoints.office.com/version'
    endpoints: str = 'https://endpoitns.office.com/endpoints/{instance}'
    changes:   str = 'https://endpoints.office.com/changes/{serviceArea}'

class formats:
    version:     string = '{YYYY}{MM}{DD}{NN}'

class validator:
    instance:    list = ['Worldwide', 'USGovDoD', 'USGovGCCHigh', 'China', 'Germany']
    serviceArea: list = ['Common', 'Exchange', 'SharePoint', 'Skype']
    category:    list = ['Optimize', 'Allow', 'Default']
    format:      list = ['JSON', 'CSV']
    impact:      list = ['AddedIp', 'AddedUrl', 'AddedIpAndUrl', 'RemovedIpOrUrl', 
                         'ChangedIsExpressRoute', 'MovedIpOrUrl', 'RemovedDuplicateIpOrUrl', 
                         'OtherNonPriorityChanges']



##### Supporting Models ######################################

class O365BaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed=True

class InstanceModel(O365BaseModel):
    instance: str
    latest:   str
    versions: List[str]

class ChangeAtomModel(O365BaseModel):
    effectiveDate: str
    ips:           list[str]
    urls:          list[str]

class ServiceAtomModel(O365BaseModel):
    serviceArea:            str
    urls:                   List[str]
    tcpPorts:               Optional[str]
    udpPorts:               Optional[str]
    category:               str
    expressRoute:           bool
    required:               bool
    notes:                  Optional[str]



##### Response Models #######################################

class VersionModel(O365BaseModel):
    instance: List[InstanceModel]

class EndpointsModel(O365BaseModel, ServiceAtomModel):
    id:                     int
    serviceAreaDisplayName: Optional[str]
    ips:                    Optional[List[str]

class ChangesModel(O365BaseModel):
    id:                     int
    endpointSetId:          int
    disposition:            str
    impact:                 str
    version:                str
    previous:               ServiceAtomModule
    current:                ServiceAtomModule
    add:                    ChangeAtomModel
    remove:                 ChangeAtomModel

    


##### Validators ############################################

def instance_validator():
    if instance not in ['Worldwide', 'USGovDoD', 'USGovGCCHigh', 'China', 'Germany']:
        raise Exception("response returned with invalide instance: %s\n" % instance)


)
##### Implementation ########################################

def version(format='JSON', AllVersions=False, Instance="Worldwide"):
    options = {
        'params': {
            'format': format
            'AllVersions': AllVersions,
            'Instance': Instance
        }
    }
    response = requests.get(URI.version, **options}
    if response.ok:
        return parse_obj_as(VersionModel, response.json())
    else:
        response.raise_for_status()
        
def endpoints(ServiceAreas=None, TenantName=None, NoIPv6=False, Instance='Worldwide'):
    If Instance not in validator.instance:
        raise Exception('unknown instance provided')
    options = {
        'params': {
            'ServiceAreas': ServiceAreas,
            'TenantName': TenantName,
            'NoIPv6': NoIPv6
        }
    }
    response = requests.get(URI.endpoints.format(Instance=Instance). **options)
    if response.ok:
        return parse_obj_as(EndpointsModel, response.json())
    else:
        response.raise_for_status()

def changes(Version='0000000000'):
    response = requests.get(URI.changes.format(Version=Version))
    if response.ok:
        return parse_obj_as(ChangesModel, response.json())
    else:
        response.raise_for_status()
