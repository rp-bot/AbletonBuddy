"""
Marvin-compatible tools for AbletonOSC Device API - device control and queries.
"""

from __future__ import annotations

from typing import Optional, Union, Annotated, List, Any
from pydantic import Field

from tools.osc.client import OSCClient


def query_device(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    device_id: Annotated[int, Field(description="Device index (0-based)")],
    query_type: Annotated[
        str,
        Field(
            description="Query type: name, class_name, type, num_parameters, parameters_name, parameters_value, parameters_min, parameters_max, parameters_is_quantized, parameter_value, parameter_value_string"
        ),
    ],
    additional_params: Annotated[
        Optional[str],
        Field(
            description="Additional params (e.g., parameter_id for parameter_value or parameter_value_string queries)"
        ),
    ] = None,
) -> str:
    """
    Query Device API properties from Ableton Live via AbletonOSC.
    Use query_type like 'name', 'class_name', 'type', 'num_parameters', etc.
    For 'parameter_value' or 'parameter_value_string' queries, provide parameter_id in additional_params.
    """
    osc = OSCClient()
    query_map = {
        # Basic device properties
        "name": "/live/device/get/name",
        "class_name": "/live/device/get/class_name",
        "type": "/live/device/get/type",
        "num_parameters": "/live/device/get/num_parameters",
        # Bulk parameter queries
        "parameters_name": "/live/device/get/parameters/name",
        "parameters_value": "/live/device/get/parameters/value",
        "parameters_min": "/live/device/get/parameters/min",
        "parameters_max": "/live/device/get/parameters/max",
        "parameters_is_quantized": "/live/device/get/parameters/is_quantized",
        # Individual parameter queries
        "parameter_value": "/live/device/get/parameter/value",
        "parameter_value_string": "/live/device/get/parameter/value_string",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    args = [track_id, device_id]

    # For individual parameter queries, add parameter_id
    if query_type.lower() in ("parameter_value", "parameter_value_string"):
        if not additional_params:
            return f"parameter_id required for query type: {query_type}"
        try:
            args.append(int(additional_params))
        except ValueError:
            return f"Invalid parameter_id: {additional_params}. Must be an integer."

    result = osc.send_and_wait(address, args)
    if result is None:
        return f"No response for query: {query_type} on track {track_id}, device {device_id}"
    return f"Track {track_id}, Device {device_id} {query_type}: {result}"


def control_device(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    device_id: Annotated[int, Field(description="Device index (0-based)")],
    command_type: Annotated[
        str,
        Field(description="Command: set_parameter_value, set_parameters_value"),
    ],
    value: Annotated[
        Union[str, int, float],
        Field(
            description="Value for the command. For set_parameters_value, provide comma-separated list of values."
        ),
    ],
    additional_params: Annotated[
        Optional[str],
        Field(
            description="Additional params (e.g., parameter_id for set_parameter_value)"
        ),
    ] = None,
) -> str:
    """
    Execute Device API setter commands via AbletonOSC.
    Use command_type like 'set_parameter_value' (individual) or 'set_parameters_value' (bulk).
    For 'set_parameter_value', provide parameter_id in additional_params.
    For 'set_parameters_value', provide comma-separated list of values in value parameter.
    """
    osc = OSCClient()
    command_map = {
        "set_parameter_value": "/live/device/set/parameter/value",
        "set_parameters_value": "/live/device/set/parameters/value",
    }

    address = command_map.get(command_type.lower())
    if not address:
        return f"Unknown command type: {command_type}. Available: {', '.join(sorted(command_map.keys()))}"

    args = [track_id, device_id]

    if command_type.lower() == "set_parameter_value":
        # Individual parameter: track_id, device_id, parameter_id, value
        if not additional_params:
            return f"parameter_id required for command: {command_type}"
        try:
            args.append(int(additional_params))
        except ValueError:
            return f"Invalid parameter_id: {additional_params}. Must be an integer."
        args.append(value)
    elif command_type.lower() == "set_parameters_value":
        # Bulk parameters: track_id, device_id, value, value, ...
        # Parse comma-separated values
        if isinstance(value, str):
            try:
                # Try to parse as comma-separated values
                value_list = [v.strip() for v in value.split(",")]
                # Try to convert to appropriate types
                parsed_values = []
                for v in value_list:
                    try:
                        # Try float first (most common for device parameters)
                        parsed_values.append(float(v))
                    except ValueError:
                        try:
                            parsed_values.append(int(v))
                        except ValueError:
                            parsed_values.append(v)
                args.extend(parsed_values)
            except Exception:
                # If parsing fails, just use the string as-is
                args.append(value)
        elif isinstance(value, (list, tuple)):
            args.extend(value)
        else:
            args.append(value)

    result = osc.send_and_wait(address, args, timeout=1.0)
    if result is None or result == "OK":
        return f"Command executed: {command_type} on track {track_id}, device {device_id} = {value}"
    return f"Command {command_type} on track {track_id}, device {device_id} result: {result}"
