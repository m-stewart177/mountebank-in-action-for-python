from typing import Iterable, Mapping, Optional, Union

from mbtest.imposters.base import JsonStructure
from mbtest.imposters import Stub, Predicate, Response, InjectionResponse, Proxy
from mbtest.imposters.behaviors import Copy, Lookup, UsingRegex
from mbtest.imposters.responses import PredicateGenerator

from furl import furl
from jinja2 import Environment, FileSystemLoader
from json import loads
from pathlib import Path

Method = Predicate.Method
Operator = Predicate.Operator
ResponseMode = Response.Mode
ProxyMode = Proxy.Mode


class StubBuilder:
    """Represents a builder of `Mountebank stub <http://www.mbtest.org/docs/api/stubs>`_.
    The builder creates an instance of :py:class:`Stub`. StubBuilders are created
    by :py:meth:`ImposterBuilder.with_stub`

    :param imposter: parent imposter to which the stub will be added
    """

    def __init__(self, imposter):
        self._predicates = []
        self._responses = []
        self._imposter = imposter

    @property
    def predicates(self):
        """Predicates used to match to incoming request. If matched
        the next response will be returned to caller.
        If there are multiple predicates all must match to send a response,
        i.e. they are logically ANDed."""
        return self._predicates

    @property
    def responses(self):
        """Response returned to caller if :py:attr:`predicates` match.
        When multiple responses are defined they are stored in a 'circular'
        buffer, i.e. they are returned in order until the last response is
        returned after which the first response is returned on the next match."""
        return self._responses

    def with_predicate(self, path: Optional[Union[str, furl]] = None,
                       method: Optional[Union[Method, str]] = None,
                       query: Optional[Mapping[str, Union[str, int, bool]]] = None,
                       body: Optional[Union[str, JsonStructure]] = None,
                       headers: Optional[Mapping[str, str]] = None,
                       xpath: Optional[str] = None,
                       operator: Union[Predicate.Operator, str] = Predicate.Operator.EQUALS,
                       case_sensitive: bool = True):
        """Add a predicate to :py:attr:`predicates`

        :param: path: URL path.
        :param method: HTTP method.
        :param query: Query arguments, keys and values.
        :param body: Body text. Can be a string, or a JSON serialisable data structure.
        :param headers: Headers, keys and values.
        :param xpath: xpath query
        :param operator:
        :param case_sensitive:
        """
        self._predicates.append(
            Predicate(path=path, method=method, query=query, body=body, headers=headers, xpath=xpath, operator=operator,
                      case_sensitive=case_sensitive))
        return self

    def with_response(self,
                      body: Union[str, JsonStructure] = "",
                      status_code: Union[int, str] = 200,
                      wait: Optional[Union[int, str]] = None,
                      repeat: Optional[int] = None,
                      headers: Optional[Mapping[str, str]] = None,
                      mode: Optional[Response.Mode] = None,
                      copy: Optional[Copy] = None,
                      decorate: Optional[str] = None,
                      lookup: Optional[Lookup] = None,
                      shell_transform: Optional[Union[str, Iterable[str]]] = None
                      ):
        """Adds a response to :py:attr:responses
        See `Mountebank 'is' response behavior <http://www.mbtest.org/docs/api/stubs>`_.

        :param body: Body text for response. Can be a string, or a JSON serialisable data structure.
        :param status_code: HTTP status code
        :param wait: `Add latency, in ms <http://www.mbtest.org/docs/api/behaviors#behavior-wait>`_.
        :param repeat: `Repeat this many times before moving on to next response
            <http://www.mbtest.org/docs/api/behaviors#behavior-repeat>`_.
        :param headers: Response HTTP headers
        :param mode: Mode - text or binary
        :param copy: Copy behavior
        :param decorate: `Decorate behavior <http://www.mbtest.org/docs/api/behaviors#behavior-decorate>`_.
        :param lookup: Lookup behavior
        :param shell_transform: shellTransform behavior
        """
        self._responses.append(
            Response(body=body, status_code=status_code, headers=headers, mode=mode, wait=wait, repeat=repeat,
                     copy=copy, decorate=decorate, lookup=lookup, shell_transform=shell_transform))
        return self

    def with_injection(self, inject):
        """ Adds a response created using Javascript code.
        See `Mountebank injection response <http://www.mbtest.org/docs/api/injection>`_.

        :param inject: JavaScript function to inject .
        """
        self._responses.append(InjectionResponse(inject))

    def with_proxy(self,
                   to: Union[furl, str],
                   wait: Optional[int] = None,
                   inject_headers: Optional[Mapping[str, str]] = None,
                   mode: "Proxy.Mode" = Proxy.Mode.ONCE,
                   predicate_generators: Optional[Iterable["PredicateGenerator"]] = None,
                   decorate: Optional[str] = None,
                   ):
        """Add a proxy response which forwards the requests and records the response.
        See `Mountebank proxy <http://www.mbtest.org/docs/api/proxies>`_.

        :param to: The origin server, to which the request should proxy.
        """
        self._responses.append(
            Proxy(to=to, wait=wait, inject_headers=inject_headers, mode=mode, predicate_generators=predicate_generators,
                  decorate=decorate))
        return self

    def add_stub(self):
        self._imposter.stubs.append(Stub(predicates=self.predicates, responses=self.responses))
        return self._imposter

    def from_template(self, template, values):
        """Create stubs using a Jinja2 template.

        :param template: template as string or a path to a template file, relative to :py:property:`templates`
        :param values: dictionary containing values used in template
"""
        template_path = Path(template)
        if Path(self._imposter.templates).joinpath(template_path).is_file():
            environment = Environment(loader=FileSystemLoader(self._imposter.templates))
            j2_template = environment.get_template(template)
        else:
            environment = Environment()
            j2_template = environment.from_string(template)

        json = j2_template.render(values)
        stubs = loads(json)
        for stub in stubs['stubs']:
            self._imposter.stubs.append(Stub.from_structure(stub))
