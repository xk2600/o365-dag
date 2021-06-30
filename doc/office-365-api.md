# Office 365 IP Address Ranges

This is a curated subset of documentation, guidance, recipes, and references
to assist in gathering real-time information about the office365 operational
state.

## Summary

> For the latest version of the Office 365 URLs and IP address ranges, use:
>  - [https://endpoints.office.com/version](#version_web_method)

> For the data on the Office 365 URLs and IP address ranges page for firewalls
> and proxy servers, use:
>  - [https://endpoints.office.com/endpoints/worldwide](#endpoints_web_method)

> To get all the latest changes since July 2018 when the web service was first 
> available, use: 
>  - [https://endpoints.office.com/changes/worldwide/0000000000](#changes_web_method)

> **NOTE** If you are using Azure ExpressRoute to connect to Office 365, please
> review Azure ExpressRoute for Office 365 to familiarize yourself with the 
> Office 365 services supported over Azure ExpressRoute. Also review the 
> article Office 365 URLs and IP address ranges to understand which network
> requests for Office 365 applications require Internet connectivity. This
> will help to better configure your perimeter security devices.

## API Interaction

###### Common Parameters

The following parameters are universal to all endpoints:

- **`format`** (*string:* `JSON` or `CSV`)

  default: the returned data format is JSON. Use this optional parameter to 
  return the data in comma-separated values (CSV) format.

- **`ClientRequestId`** (*guid*)

  A required GUID that you generate for client association. Generate a unique 
  GUID for each machine that calls the web service (the scripts included on this
  page generate a GUID for you). Do not use the GUIDs shown in the following
  examples because they might be blocked by the web service in the future. GUID 
  format is xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, where x represents a hexadecimal
  number.


### Version Web Method
[https://endpoints.office.com/version](#version_web_method)

###### Parameters

- **`AllVersions`** (*boolean:* `true` or `false`)
   
  By default, the version returned is the latest. Include this optional
  parameter to request all published versions since the web service was first
  released.

- **`Format`** (*string:* `JSON`, `CSV`, `RSS`)

  In addition to the JSON and CSV formats, the version web method also supports
  RSS. You can use this optional parameter along with the AllVersions=true
  parameter to request an RSS feed that can be used with Outlook or other RSS 
  readers.

- **`Instance`** (*string:* `Worldwide`, `China`, `Germany`, `USGovDoD`, `USGovGCCHigh`)

  This optional parameter specifies the instance to return the version for. If
  omitted, all instances are returned. Valid instances are: Worldwide, China, 
  Germany, USGovDoD, USGovGCCHigh.

###### Response Fields

| Field     | Description
|-----------|-------------------------------------------------------------
|`instance` | *string:* The short name of the Office 365 service instance
|`latest`   | *YYYMMDDNN*: The latest version for endpoints of the specified instance
|`versions` | *[YYYMMDDNN,...]:* list of all previous versions for the specified instance


###### Example Response

```
[
 {
  "instance": "Worldwide",
  "latest": "2018063000"
 },
 {
  "instance": "USGovDoD",
  "latest": "2018063000"
 },
 {
  "instance": "USGovGCCHigh",
  "latest": "2018063000"
 },
 {
  "instance": "China",
  "latest": "2018063000"
 },
 {
  "instance": "Germany",
  "latest": "2018063000"
 }
]
```


### Endpoints Web Method
[https://endpoints.office.com/endpoints/worldwide](#endpoints_web_method)


###### Parameters

- **`ServiceAreas`** (*string:* `Common`, `Exchange`, `SharePoint`, `Skype`) 

  A comma-separated list of service areas. Valid items are Common, Exchange,
  SharePoint, and Skype. Because Common service area items are a prerequisite
  for all other service areas, the web service always includes them. If you do
  not include this parameter, all service areas are returned.
  
- **`TenantName`** (*string*: `Acme`)

  Your Office 365 tenant name. The web service takes your provided name and
  inserts it in parts of URLs that include the tenant name. If you don't 
  provide a tenant name, those parts of URLs have the wildcard character (\*).

- **`NoIPv6`** (*boolean:* `true` or false`)

  Set the value to true to exclude IPv6 addresses from the output if you don't
  use IPv6 in your network.

- **`Instance`** (*string:* `Worldwide`, `China`, `Germany`, `USGovDoD`, `USGovGCCHigh`)

  This required parameter specifies the instance from which to return the
  endpoints. Valid instances are: Worldwide, China, Germany, USGovDoD, and 
  USGovGCCHigh.

###### Response Fields

| Field         | Description
|---------------|---------------------------------------------------------------
|`id`           | immutable id number of the endpoint set.
|`serviceArea`  | *string:* service area: `Common`, `Exchange`, `SharePoint`, or `Skype`
|`urls`         | *[string,..]:* JSON array of DNS records
|`tcpPorts`     | comma separated list of hyphenated TCP port ranges
|`udpPorts`     | comma separated list of hyphenated UDP port ranges
|`ips`          | json array of ip ranges associated with TCP or UDP ports
|`category`     | *string:* `Optimize`, `Allow`, and `Default`
|`expressRoute` | *boolean:* True destinations routed over ExpressRoute, otherwise false
|`required`     | *boolean:& True: endpoint set requires connectivity for support, otehrwise false
|`notes`        | describes Office 365 functionality unavailable without updates as perscribed 

###### Example Request and Response

```
GET https://endpoints.office.com/endpoints/Worldwide?ClientRequestId=b10c5ed1-bad1-445f-b386-b919946339a7
...

```

```
200 OK
[
 {
  "id": 1,
  "serviceArea": "Exchange",
  "serviceAreaDisplayName": "Exchange Online",
  "urls":
   [
    "*.protection.outlook.com"
   ],
  "ips":
   [
    "2a01:111:f403::/48", "23.103.132.0/22", "23.103.136.0/21", "23.103.198.0/23", 
    "23.103.212.0/22", "40.92.0.0/14", "40.107.0.0/17", "40.107.128.0/18", 
    "52.100.0.0/14", "213.199.154.0/24", "213.199.180.128/26", "94.245.120.64/26",
    "207.46.163.0/24", "65.55.88.0/24", "216.32.180.0/23", "23.103.144.0/20", 
    "65.55.169.0/24", "207.46.100.0/24", "2a01:111:f400:7c00::/54", 
    "157.56.110.0/23", "23.103.200.0/22", "104.47.0.0/17", 
    "2a01:111:f400:fc00::/54", "157.55.234.0/24", "157.56.112.0/24", 
    "52.238.78.88/32"
   ],
  "tcpPorts": "443",
  "expressRoute": true,
  "category": "Allow"
 },
 ...removed for brevity...
}
```


### Changes Web Method
[https://endpoints.office.com/changes/worldwide/0000000000](#changes_web_method)

###### Parameters

- **`Version`** (*string:* `YYYYMMDDNN`)

  Required URL route parameter. This value is the version that you have 
  currently implemented. The web service will return the changes since that
  version. The format is `YYYYMMDDNN`, where `NN` is a natural number 
  incremented if there are multiple versions required to be published on a 
  single day, with `00` representing the first update for a given day. The 
  web service requires the version parameter to contain exactly 10 digits.

###### Response Fields

| Field            | Description                                  
|------------------|-----------------------------------------------------------
|`id`              | The immutable id of the change record.
|`endpointSetId`   | The ID of the endpoint set record that is changed.
|`disposition`     | `change`, `add`, or `remove`.
|`impact`          | `AddedIp`, `AddedUrl`, `AddedIpAndUrl`, `RemovedIpOrUrl`, `ChangedIsExpressRoute`, `MovedIpOrUrl``RemovedDuplicateIpOrUrl`, `OtherNonPriorityChanges`
|`version`         | `YYYYMMDDNN`, where `NN` is incremented for intraday changes
|`previous`        | previous values of changed elements on the endpoint set **deprecated**
|`current`         | updated values of changeds elements on the endpoint set
|`add`             | substructure: `effectiveDate`, `ips`, `urls`
|`remove`          | substructure: `effectiveDate`, `ips`, `urls`

###### Response Sub-fields used in `add` and `remove`:

| Sub-Fields    | Descriptions
|---------------|-----------------------------------------------------------
|`effectiveDate`| Defines the data when the additions will be live in the service.
|`ips`          | Items to be added/removed from the ips array. 
|`urls`         | Items to be added/removed from the urls array.

###### `current` and `previous` fields include the following subfields: 

| Sub-Fields    | Descriptions
|---------------|-----------------------------------------------------------
|`serviceArea`  | *string:* service area: `Common`, `Exchange`, `SharePoint`, or `Skype`
|`tcpPorts`     | comma separated list of hyphenated TCP port ranges
|`udpPorts`     | comma separated list of hyphenated UDP port ranges
|`category`     | *string:* `Optimize`, `Allow`, and `Default`
|`expressRoute` | *boolean:* True destinations routed over ExpressRoute, otherwise false
|`required`     | *boolean:& True: endpoint set requires connectivity for support, otehrwise false
|`notes`        | describes Office 365 functionality unavailable without updates as perscribed 

###### Example Response

```
GET https://endpoints.office.com/changes/worldwide/0000000000?ClientRequestId=b10c5ed1-bad1-445f-b386-b919946339a7
```

```
200 OK
[
 {
  "id": 424,
  "endpointSetId": 32,
  "disposition": "Change",
  "version": "2018062700",
  "remove":
   {
    "urls":
     [
      "*.api.skype.com", "skypegraph.skype.com"
     ]
   }
 },
 {
 "id": 426,
 "endpointSetId": 31,
 "disposition": "Change",
 "version": "2018062700",
 "add":
  {
   "effectiveDate": "20180609",
   "ips":
    [
     "51.140.203.190/32"
    ]
  },
```


## Reference

1. [Office 365 IP Address Ranges](https://github.com/MicrosoftDocs/microsoft-365-docs/blob/public/microsoft-365/enterprise/urls-and-ip-address-ranges.md)
2. [Office 365 Endpoints](https://github.com/MicrosoftDocs/microsoft-365-docs/blob/public/microsoft-365/enterprise/managing-office-365-endpoints.md)
3. [Office 365 IP Web Service](https://github.com/MicrosoftDocs/microsoft-365-docs/blob/public/microsoft-365/enterprise/microsoft-365-ip-web-service.md)
