from typing import Dict, Union, Tuple

UriParams = Dict[str, str]
Headers = Dict[str, str]
EncryptionContext = Dict[str, str]
ApiGatewayHttpResponse = Dict[str, Union[Dict[str, str], str, int]]
ReceiverArgs = Tuple[str, str, int, Headers]
EnvLookup = Dict[str, Union[str, bool, int, None]]
