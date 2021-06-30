# Palo Alto Networks - External Dynamic Lists

The following is a currated/copied set of notes relevant to understanding,
deploying, and operating Palo Alto Firewalls which leverage External Dynamic
Lists for application of policy, exceptions, and url filters.

> **NOTICE:** EDLs while powerful are only one of many ways to make policy
> more dynamic and robust. It may behoove the individual implementing to
> evaluate and compare this feature against leveraging the XML API on both
> the Palo Alto Firewall or Panorama or determining if the use-case can be
> solved with the User-ID agent, VMware Plugins, Cisco Plugins, or Auto-Tag
> functionality.

> **WARNING:** There are strict limits to the length of the list, how many
> lists can be active at once on specific appliances, the time the server
> takes to respond with the list, etc. These limits will most likely change
> over time, so please evaluate these limitations before solidifying your 
> design so as to not find out the policy is broken due to this. Talk to
> your Sales Engineer, call Palo Alto TAC, or reach out to me and I would be
> happy to find and share the information.

## What are External Dynamical Lists

An External Dynamic List is a text file that is hosted on an external web 
server so that the firewall can import objects—IP addresses, URLs, domains—
included in the list and enforce policy. To enforce policy on the entries 
included in the external dynamic list, you must reference the list in a 
supported policy rule or profile. As you modify the list, the firewall 
dynamically imports the list at the configured interval and enforces policy 
without the need to make a configuration change or a commit on the firewall. If 
the web server is unreachable, the firewall uses the last successfully retrieved 
list for enforcing policy until the connection is restored with the web server. 
In cases where authentication to the EDL fails, the security policy stops 
enforcing the EDL. To retrieve the external dynamic list, the firewall uses the 
interface configured with the Palo Alto Networks Services
service route, which is the management interface by default. You can also 
customize the Service Routes you’d like the firewall to use.

#### The firewall supports four types of external dynamic lists:

- IP Address

  The firewall typically enforces policy for a source or destination IP 
  address that is defined as a static object on the firewall (see Enforce 
  Policy on an External Dynamic List) If you need agility in enforcing policy 
  for a list of source or destination IP addresses that emerge ad hoc, you can 
  use an external dynamic list of type IP address as a source or destination 
  address object in policy rules, and configure the firewall to deny or allow 
  access to the IP addresses (IPv4 and IPv6 address, IP range and IP subnets) 
  included in the list. The firewall treats an external dynamic list of type 
  IP address as an address object; all the IP addresses included in a list are 
  handled as one address object.

- Predefined IP Address

  A predefined IP address list is a type of IP address list that refers to any
  of the two Palo Alto Networks Malicious IP Address Feeds that have fixed or
  “predefined” contents. These feeds are automatically added to your firewall
  if you have an active Threat Prevention license. A predefined IP address
  list can also refer to any external dynamic list you create that uses a Palo 
  Alto Networks IP address feed as a source.

- URL

  An external dynamic list of type URL gives you the agility to protect your 
  network from new sources of threat or malware. The firewall handles an
  external dynamic list with URLs like a custom URL category and you can use
  this list in two ways:

  1. As a match criteria in Security policy rules, Decryption policy rules, and
     QoS policy rules to allow, deny, decrypt, not decrypt, or allocate bandwidth
     for the URLs in the custom category.

  2. In a URL Filtering profile where you can define more granular actions, such
     as continue, alert, or override, before you attach the profile to a Security
     policy rule (see Use an External Dynamic List in a URL Filtering Profile).

- Domain

  An external dynamic list of type domain allows you to import custom domain
  names into the firewall to enforce policy using an Anti-Spyware profile. This
  capability is very useful if you subscribe to third-party threat intelligence
  feeds and want to protect your network from new sources of threat or malware
  as soon as you learn of a malicious domain. For each domain you include in the
  external dynamic list, the firewall creates a custom DNS-based spyware 
  signature so that you can enable DNS sinkholing. The DNS-based spyware 
  signature is of type spyware with medium severity and each signature is named
  Custom Malicious DNS Query <domainname>

  > For details, see *Configure DNS Sinkholing* for a List of Custom Domains.

On each firewall model, you can use a maximum of 30 external dynamic lists with
unique sources to enforce policy; predefined IP address feeds do not count 
toward this limit. The external dynamic list limit is not applicable to
Panorama. When using Panorama to manage a firewall that is enabled for multiple
virtual systems, if you exceed the limit for the firewall, a commit error 
displays on Panorama. A source is a URL that includes the IP address or 
hostname, the path, and the filename for the external dynamic list. The firewall
matches the URL (complete string) to determine whether a source is unique.

While the firewall does not impose a limit on the number of lists of a specific 
type, the following limits are enforced:

- IP address

  The PA-5000 Series, PA-5200 Series, and the PA-7000 Series 
  firewalls support a maximum of 150,000 total IP addresses; all other models 
  support amaximum of 50,000 total IP addresses. No limits are enforced for 
  the number of IP addresses per list. When the maximum supported IP address 
  limit is reached on the firewall, the firewall generates a syslog message. 
  The IP addresses in predefined IP address lists do not count toward the limit.

- URL and domain

  A maximum of 50,000 URLs and 50,000 domains are supported on
  each model, with no limits enforced on the number of entries per list.

List entries only count toward the firewall limits if they belong to an external
dynamic list that is referenced in policy.

> - When parsing the list, the firewall skips entries that do not match the list 
>   type, and ignores entries that exceed the maximum number supported for the
>   model. To ensure that the entries do not exceed the limit, check the number of
>   entries currently used in policy. Select Objects -> External Dynamic Lists ->
>   and click List Capacities
>
> - An external dynamic list should not be empty. If you want to stop using the 
>   list, remove the reference from the policy rule or profile rather than leave 
>   the list empty. If the the list is empty the firewall fails to refresh the 
>   list and continues to use the last information it retrieved.

## Retrieve an External Dynamic List from the Web Server

When you Configure the Firewall to Access an External Dynamic List, you can
configure the firewall to retrieve the list from the web server on an hourly 
(default)five minute, daily, weekly, or monthly basis. If you have added or 
deleted IP addresses from the list and need to trigger an immediate refresh, 
use the following process to fetch the updated list.

1. To retrieve the list on demand, select `Objects` > `External Dynamic Lists`.
2. Select the list that you want to refresh, and click `Import Now`. The job to
   import the list is queued.
3. To view the status of the job in the Task Manager, see Manage and Monitor
   Administrative Tasks.
4. *(Optional)* After the firewall retrieves the list, View External Dynamic List
   Entries.

   1. Select `Objects` > `External Dynamic Lists`.
   2. Click the external dynamic list you want to view.
   3. Click List `Entries and Exceptions` and view the objects that the 
      firewall retrieved from the list.

      > The list might be empty if:
      >
      > - The EDL has not yet been applied to a Security policy rule. To apply an
      >   to a Security policy rule and populate the EDL, see Enforce Policy on an
      >   External Dynamic List.
      >
      > - The firewall has not yet retrieved the external dynamic list. To force 
      >   the firewall to retrieve an external dynamic list immediately, Retrieve
      >   an External Dynamic List from the Web Server.
      >
      > - The firewall is unable to access the server that hosts the external 
      >   dynamic list. Click Test Source URL to verify that the firewall can
      >   connect to the server.

   4. Enter an IP address, domain, or URL (depending on the type of list) in the 
      filter field and Apply Filter ( ) to check if it’s in the list. Exclude 
      Entries from an External Dynamic List based on which IP addresses, domains, 
      and URLs you need to block or allow.

   5. *(Optional)* View the AutoFocus Intelligence Summary for a list entry.
      Hover over an entry to open the drop-down and then click `AutoFocus`.


## Enforce Policy on an External Dynamic List

Block or allow traffic based on IP addresses or URLs in an external dynamic list, 
or use an dynamic domain list with a DNS sinkhole to prevent access to malicious
domains. Refer to the table below for the ways you can use external dynamic lists 
to enforce policy on the firewall.

- Configure DNS Sinkholing for a List of Custom Domains.
- Use an External Dynamic List in a URL Filtering Profile.
- Use an External Dynamic List of Type URL as Match Criteria in a Security Policy Rule.

  1. Select `Policies` > `Security`.
  2. Click `Add` and enter a descriptive Name for the rule.
  3. In the `Source` tab, select the `Source Zone`.
  4. In the `Destination` tab, select the `Destination Zone`.
  5. In the `Service/URL Category` tab, click `Add` to select the appropriate 
     external dynamic list from the URL Category list.
  6. In the `Actions` tab, set the `Action Setting` to `Allow` or `Deny`.
  7. Click `OK` and `Commit`.
  8. Verify whether entries in the external dynamic list were ignored or skipped.

     Use the following CLI command on a firewall to review the details for a list.

     `request system external-list show type <domain|ip|url> name_of_list`
      
     For example:

     `request system external-list show type url EBL_ISAC_Alert_List`

  9. Test that the policy action is enforced.

     1. View External Dynamic List Entries for the URL list, and attempt to 
        access a URL from the list.

     2. Verify that the action you defined is enforced.

     3. To monitor the activity on the firewall:

        - Select `ACC` and add a URL Domain as a global filter to view the 
          Network Activity and Blocked Activity for the URL you accessed.

        - Select `Monitor` > `Logs` > `URL Filtering.` to access the detailed 
          log view.
          
- Use an External Dynamic List of Type IP or Predefined IP as a Source or
  Destination Address Object in a Security Policy Rule.

- This capability is useful if you deploy new servers and want to allow access
  to the newly deployed servers without requiring a firewall commit.

  1. Select `Policies` > `Security`.
  2. Click `Add` and give the rule a descriptive name in the General tab.
  3. In the `Source` tab, select the `Source Zone` and optionally select the
     external dynamic list as the Source Address.

  4. In the `Destination` tab, select the `Destination Zone` and optionally 
     select the external dynamic list as the Destination Address.

  5. In the `Service/ URL Category` tab, make sure the `Service` is set to 
     `application-default`.
  6. In the `Actions` tab, set the `Action Setting` to `Allow` or `Deny`.

     > Create separate external dynamic lists if you want to specify allow 
     > and deny actions for specific IP addresses.

  7. Leave all the other options at the default values.
  8. Click `OK` to save the changes.
  9. `Commit` the changes.
 10. Test that the policy action is enforced.

     1. View External Dynamic List Entries for the external dynamic list, 
        and attempt to access an IP address from the list.

     2. Verify that the action you defined is enforced.

     3. Select `Monitor` > `Logs` > `Traffic` and view the log entry for the 
        session.

     4. To verify the policy rule that matches a flow, use the following CLI
        command:

        `test security-policy-match source <IP> destination <IP> destination port # protocol <#>`

        > Tips for enforcing policy on the firewall with external dynamic 
        > lists:
        >
        > - When viewing external dynamic lists on the firewall (`Objects` >
        >   `External Dynamic Lists`), click `List Capacities` to compare how 
        >   many IP addresses, domains, and URLs are currently used in policy
        >   with the total number of entries that the firewall supports for 
        >   each list type.
        > - Use Global Find to Search the Firewall or Panorama Management
        >   Server for a domain, IP address, or URL that belongs to one or more
        >   external dynamic lists is used in policy. This is useful for
        >   determining which external dynamic list (referenced in a Security 
        >   policy rule) is causing the firewall to block or allow a certain
        >   domain, IP address, or URL.

## External Dynamic List Exmaples:

###### IP address list

- The external dynamic list can include:
  - individual IP addresses
  - subnet addresses (address/mask)
  - range of IP addresses 

> In addition, the block list can include comments and special characters such
> as `*`, `:`, `;`, `#`, `/`.

The syntax for each line in the list is:
`ipAddr`|`ipAddr/prefixLength`|`ipStartRange-ipEndRange`  `space`  `comment`

- Enter each IP address/range/subnet in a new line
- URLs or domains are not supported in this list.

> A subnet or an IP address range, such as 192.168.20.0/24 or
> 192.168.20.40-192.168.20.50, count as one IP address entry and not as
> multiple IP addresses.

> **NOTE:** If you add comments, the comment must be on the same line as the
> IP address/range/subnet. The space at the end of the IP address is the 
> delimiter that separates a comment from the IP address.

```
192.168.20.10/32 
 2001:db8:123:1::1 #test IPv6 address 
 192.168.20.0/24 ; test internal subnet 
 2001:db8:123:1::/64 test internal IPv6 range 
 192.168.20.40-192.168.20.50
```

###### Domain list

- Enter each domain name in a new line
- **URLs or IP addresses are not supported in this list.**
- Do **NOT** prefix the domain name with the protocol, http:// or https://.
- **Wildcards are not supported.**
- Each domain entry can be up to **255 characters** in length.

```
www.example.com
 baddomain.com
 qqq.abcedfg.au
```

## References

 1. External Dynamic List Summary - [paloaltonetworks.com](https://docs.paloaltonetworks.com/pan-os/8-1/pan-os-admin/policy/use-an-external-dynamic-list-in-policy/external-dynamic-list.html#idf36cb80a-77f1-4d17-9c4b-7efe9fe426af*)

 2. Configuration and Validation of an EDL - [paloaltonetworks.com](https://docs.paloaltonetworks.com/pan-os/8-1/pan-os-admin/policy/use-an-external-dynamic-list-in-policy/enforce-policy-on-an-external-dynamic-list.html#id65d71322-1c04-4eb7-ab66-4d9bb3f41a52_idc5286843-e97b-4cdd-9b56-fce0d2b4d035)

 3. Formatting Guidelines - [paloaltonetworks.com](https://docs.paloaltonetworks.com/pan-os/8-1/pan-os-admin/policy/use-an-external-dynamic-list-in-policy/formatting-guidelines-for-an-external-dynamic-list/ip-address-list.html#idd44a975a-a94a-4398-864e-5cf223f1d351)
