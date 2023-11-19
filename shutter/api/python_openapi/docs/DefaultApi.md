# openapi_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_server_status_status_get**](DefaultApi.md#get_server_status_status_get) | **GET** /status | Get Server Status
[**get_shutter_list_get**](DefaultApi.md#get_shutter_list_get) | **GET** / | Get Shutter List
[**get_shutter_state_shutter_name_get**](DefaultApi.md#get_shutter_state_shutter_name_get) | **GET** /{shutter_name} | Get Shutter State
[**login_for_access_token_token_post**](DefaultApi.md#login_for_access_token_token_post) | **POST** /token | Login For Access Token
[**set_shutter_state_shutter_name_post**](DefaultApi.md#set_shutter_state_shutter_name_post) | **POST** /{shutter_name} | Set Shutter State


# **get_server_status_status_get**
> ServerStatusReport get_server_status_status_get()

Get Server Status

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.server_status_report import ServerStatusReport
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)

    try:
        # Get Server Status
        api_response = api_instance.get_server_status_status_get()
        print("The response of DefaultApi->get_server_status_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_server_status_status_get: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**ServerStatusReport**](ServerStatusReport.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_shutter_list_get**
> ShutterChannelList get_shutter_list_get()

Get Shutter List

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.shutter_channel_list import ShutterChannelList
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)

    try:
        # Get Shutter List
        api_response = api_instance.get_shutter_list_get()
        print("The response of DefaultApi->get_shutter_list_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_shutter_list_get: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**ShutterChannelList**](ShutterChannelList.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_shutter_state_shutter_name_get**
> ShutterStateReport get_shutter_state_shutter_name_get(shutter_name)

Get Shutter State

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.shutter_state_report import ShutterStateReport
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    shutter_name = 'shutter_name_example' # str | 

    try:
        # Get Shutter State
        api_response = api_instance.get_shutter_state_shutter_name_get(shutter_name)
        print("The response of DefaultApi->get_shutter_state_shutter_name_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_shutter_state_shutter_name_get: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shutter_name** | **str**|  | 

### Return type

[**ShutterStateReport**](ShutterStateReport.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **login_for_access_token_token_post**
> Token login_for_access_token_token_post(username, password, grant_type=grant_type, scope=scope, client_id=client_id, client_secret=client_secret)

Login For Access Token

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.token import Token
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    username = 'username_example' # str | 
    password = 'password_example' # str | 
    grant_type = 'grant_type_example' # str |  (optional)
    scope = '' # str |  (optional) (default to '')
    client_id = 'client_id_example' # str |  (optional)
    client_secret = 'client_secret_example' # str |  (optional)

    try:
        # Login For Access Token
        api_response = api_instance.login_for_access_token_token_post(username, password, grant_type=grant_type, scope=scope, client_id=client_id, client_secret=client_secret)
        print("The response of DefaultApi->login_for_access_token_token_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->login_for_access_token_token_post: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 
 **password** | **str**|  | 
 **grant_type** | **str**|  | [optional] 
 **scope** | **str**|  | [optional] [default to &#39;&#39;]
 **client_id** | **str**|  | [optional] 
 **client_secret** | **str**|  | [optional] 

### Return type

[**Token**](Token.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_shutter_state_shutter_name_post**
> ShutterStateReport set_shutter_state_shutter_name_post(shutter_name, shutter_channel_operation)

Set Shutter State

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.shutter_channel_operation import ShutterChannelOperation
from openapi_client.models.shutter_state_report import ShutterStateReport
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    shutter_name = 'shutter_name_example' # str | 
    shutter_channel_operation = openapi_client.ShutterChannelOperation() # ShutterChannelOperation | 

    try:
        # Set Shutter State
        api_response = api_instance.set_shutter_state_shutter_name_post(shutter_name, shutter_channel_operation)
        print("The response of DefaultApi->set_shutter_state_shutter_name_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->set_shutter_state_shutter_name_post: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shutter_name** | **str**|  | 
 **shutter_channel_operation** | [**ShutterChannelOperation**](ShutterChannelOperation.md)|  | 

### Return type

[**ShutterStateReport**](ShutterStateReport.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

