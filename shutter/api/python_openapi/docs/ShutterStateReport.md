# ShutterStateReport


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**shutter_name** | **str** |  | 
**state** | [**ShutterState**](ShutterState.md) |  | 

## Example

```python
from openapi_client.models.shutter_state_report import ShutterStateReport

# TODO update the JSON string below
json = "{}"
# create an instance of ShutterStateReport from a JSON string
shutter_state_report_instance = ShutterStateReport.from_json(json)
# print the JSON string representation of the object
print ShutterStateReport.to_json()

# convert the object into a dict
shutter_state_report_dict = shutter_state_report_instance.to_dict()
# create an instance of ShutterStateReport from a dict
shutter_state_report_form_dict = shutter_state_report.from_dict(shutter_state_report_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


