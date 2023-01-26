from typing import Mapping, Optional, Union

from mbtest.imposters.base import JsonStructure
from mbtest.imposters import Imposter, Response
from mbtest.imposters.responses import HttpResponse

from .stub_builder import StubBuilder

Protocol = Imposter.Protocol


class ImposterBuilder:
    def __init__(self, port: Optional[int] = None, protocol: Imposter.Protocol = Imposter.Protocol.HTTP,
                 name: Optional[str] = None):
        self._port = port
        self._protocol = protocol
        self._name = name
        self._stubs = []
        self._default_response = None

    @property
    def port(self):
        return self._port

    @property
    def protocol(self):
        return self._protocol

    @property
    def name(self):
        return self._name

    @property
    def stubs(self):
        return self._stubs

    def with_stub(self):
        return StubBuilder(self)

    def with_default(self,
                     body: Union[str, JsonStructure] = "",
                     status_code: Union[int, str] = 200,
                     headers: Optional[Mapping[str, str]] = None,
                     mode: Optional[Response.Mode] = None):
        self._default_response = HttpResponse(body=body, status_code=status_code, headers=headers, mode=mode)
        return self

    def from_template(self, package, template):
        pass

    def create(self):
        return Imposter(port=self.port, protocol=self.protocol, name=self.name, stubs=self.stubs,
                        default_response=self._default_response)
