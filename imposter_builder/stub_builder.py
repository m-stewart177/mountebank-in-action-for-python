from typing import Iterable, Mapping, Optional, Union

from furl import furl

from mbtest.imposters.base import JsonStructure
from mbtest.imposters import Stub, Predicate, Response, InjectionResponse, Proxy
from mbtest.imposters.behaviors import Copy, Lookup
from mbtest.imposters.responses import PredicateGenerator

Method = Predicate.Method
Operator = Predicate.Operator
ResponseMode = Response.Mode
ProxyMode = Proxy.Mode


class StubBuilder:
    def __init__(self, imposter):
        self._predicates = []
        self._responses = []
        self._imposter = imposter

    @property
    def predicates(self):
        return self._predicates

    @property
    def responses(self):
        return self._responses

    def with_predicate(self, path: Optional[Union[str, furl]] = None,
                       method: Optional[Union[Method, str]] = None,
                       query: Optional[Mapping[str, Union[str, int, bool]]] = None,
                       body: Optional[Union[str, JsonStructure]] = None,
                       headers: Optional[Mapping[str, str]] = None,
                       xpath: Optional[str] = None,
                       operator: Union[Predicate.Operator, str] = Predicate.Operator.EQUALS,
                       case_sensitive: bool = True):
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
        self._responses.append(
            Response(body=body, status_code=status_code, headers=headers, mode=mode, wait=wait, repeat=repeat,
                     copy=copy, decorate=decorate, lookup=lookup, shell_transform=shell_transform))
        return self

    def with_injection(self, inject):
        self._responses.append(InjectionResponse(inject))

    def with_proxy(self,
                   to: Union[furl, str],
                   wait: Optional[int] = None,
                   inject_headers: Optional[Mapping[str, str]] = None,
                   mode: "Proxy.Mode" = Proxy.Mode.ONCE,
                   predicate_generators: Optional[Iterable["PredicateGenerator"]] = None,
                   decorate: Optional[str] = None,
                   ):
        self._responses.append(
            Proxy(to=to, wait=wait, inject_headers=inject_headers, mode=mode, predicate_generators=predicate_generators,
                  decorate=decorate))
        return self

    def add_stub(self):
        self._imposter.stubs.append(Stub(predicates=self.predicates, responses=self.responses))
        return self._imposter
