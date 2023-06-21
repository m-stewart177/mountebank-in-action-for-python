from typing import Mapping, Optional, Union

from mbtest.imposters.base import JsonStructure
from mbtest.imposters import Imposter, Response
from mbtest.imposters.responses import HttpResponse

from jinja2 import Environment, FileSystemLoader
from json import loads
from os import getcwd
from pathlib import Path

from .stub_builder import StubBuilder

Protocol = Imposter.Protocol


class ImposterBuilder:
    """Represents a builder class of `Mountebank imposter <http://www.mbtest.org/docs/api/mocks>`_.
    The builder creates an instance of :py:class:`Imposter`

    :param port: Port.
    :param protocol: Protocol to run on.
    :param name: Imposter name - useful for interactive exploration of imposters on http://localhost:2525/imposters
    :param templates: Path to root folder containing Jinja2 templates for creating complex imposters
    """
    _templates = Path(getcwd())

    def __init__(self, port: Optional[int] = None, protocol: Imposter.Protocol = Imposter.Protocol.HTTP,
                 name: Optional[str] = None, templates: Optional[str] = getcwd()):
        self._port = port
        self._protocol = protocol
        self._name = name
        self._stubs = []
        self._default_response = None
        self._templates = templates

    @property
    def port(self):
        """Imposter is attached to a running MB server."""
        return self._port

    @property
    def protocol(self):
        """Imposter responds to on a running MB server"""
        return self._protocol

    @property
    def name(self):
        """Name included in log entries relating to this imposter"""
        return self._name

    @property
    def stubs(self):
        """List of stubs defined to imposter"""
        return self._stubs

    @property
    def templates(self):
        """Path to root folder of templates"""
        return self._templates

    @templates.setter
    def templates(self, value):
        """Set a path to root folder for templates, if not the current working directory

        :param value: Path to templates root folder"""
        self._templates = value

    def with_stub(self):
        """Start a new stub"""
        return StubBuilder(self)

    def with_default(self,
                     body: Union[str, JsonStructure] = "",
                     status_code: Union[int, str] = 200,
                     headers: Optional[Mapping[str, str]] = None,
                     mode: Optional[Response.Mode] = None):
        """Define a default stub returned if no other stub matches

        :param body: Body text for response. Can be a string, or a JSON serialisable data structure.
        :param status_code:  HTTP status code
        :param headers: Response HTTP headers
        :param mode: Mode - text or binary
        """
        self._default_response = HttpResponse(body=body, status_code=status_code, headers=headers, mode=mode)
        return self

    def from_template(self, template: Optional[str], values: Optional[dict]):
        """Create an imposter from a Jinja2 template

        :param template: template as string or a path to a template file, relative to :py:property:`templates`
        :param values: dictionary containing values used in template
        """
        template_path = Path(template)
        if Path(self.templates).joinpath(template_path).is_file():
            environment = Environment(loader=FileSystemLoader(self.templates))
            j2_template = environment.get_template(template)
        else:
            environment = Environment()
            j2_template = environment.from_string(template)

        imposter_definition = loads(j2_template.render(values))

        return Imposter(port=self.port, protocol=self.protocol, name=self.name, stubs=self.stubs,
                        default_response=self._default_response).from_structure(imposter_definition)

    def create(self):
        """Create an :py:class:`Imposter` object"""
        return Imposter(port=self.port, protocol=self.protocol, name=self.name, stubs=self.stubs,
                        default_response=self._default_response)
