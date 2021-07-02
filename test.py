import json
import unittest
from unittest.mock import patch
from requests.models import Response
import o365ipAddr

def get_mockup_responses(kwargs_dictlist):
    from requests import get
    mockup_content = {}
    for kwargs in kwargs_dictlist:
        for template_uri in o365ipAddr.URI.__class__.__dict__.keys() if key[0] != '_':
            uri = template_uri.foramt(**kwargs)
            resp = get(uri)
            if resp.ok:
                testcase_content[uri] = resp._content

def update_mockup_content_file():
    f = open('mockup_responses.json', 'w')
    paramsDict = {}
    for name in o365ipAddr.__dict__:
        if isinstance(getattr(o365ipAddr, name), o365ipAddr.RestParameter):
            param = getattr(o365ipAddr, name)
            paramsDict[name] = 
            for option in dir(param):
                paramsDict[name]

                



        


"""
Mock requests' response object.
"""
class RequestsMock:
    mockups = {}

    class MockResponse:
        def __init__(self, status_code, json_data = None, csv_data = None):
            self.json_data   = json_data
            self.csv_data    = csv_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def text(self):
            return self.csv_data

        def raise_for_status():
            pass

    def __get__(self, v):
        [ key for key in URI.__class__.__dict__.keys() if key[0] != '_' ] 


    def fget(*args, **kwargs):
        if mockup in mockups:
            return MockReesponse(**mockup)
        else return MockResponse(404)
        

requests = RequestsMock



class testO365ipAddr(unittest.TestCase):
    """ 
    Unittests for o365ipAddr module
    """
    def test_version(self):
        """ Test o365ipAddr.getVersion without args """
        








    def test(function, **args, **kwargs):
        module = function.__module__
        name   = function.__name__
        obj    = function(*args, **kwargs)
        pObj   = pformat(f.obj)
        print(f"{module}.{name}() ->\n  {obj}"

    print(
        '### Running system tests: ##########################################\n'
        '#\n'
        '# Version Tests:\n\n', end='')

    test(getEndpoints)
    test(getEndpoints, )

    print('')

if __name__ == '__main__':
