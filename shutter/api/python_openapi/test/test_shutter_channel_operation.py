# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from openapi_client.models.shutter_channel_operation import ShutterChannelOperation

class TestShutterChannelOperation(unittest.TestCase):
    """ShutterChannelOperation unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ShutterChannelOperation:
        """Test ShutterChannelOperation
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ShutterChannelOperation`
        """
        model = ShutterChannelOperation()
        if include_optional:
            return ShutterChannelOperation(
                action = 'ON'
            )
        else:
            return ShutterChannelOperation(
                action = 'ON',
        )
        """

    def testShutterChannelOperation(self):
        """Test ShutterChannelOperation"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
