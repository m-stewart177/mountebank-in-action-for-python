## Imposter Builder: create `mountebank` imposters using Python

The `imposter-builder` package builds on `mbtest` https://pypi.org/project/mbtest/ 
to provide builder classes to help create `mountebank` imposters http://www.mbtest.org/.

An imposter (or mock) is described in detail [here](http://www.mbtest.org/docs/api/mocks).
When using `mountebank` imposters are created by posting a description of it as json to
the `mountebank` server (typically listening to port 2525).

An imposter consists of at least the **port** it will listen and the network **protocol** 
it will use. It can also have an optional **name**, the name is used by `mountebank` in 
the logs it produces to identify entries related to the imposter.

An imposter to be useful must respond to requests, to do this an imposter has one or more 
**stubs**. A stub is defined by **predicates**, a pattern which described the requests to
respond to and **responses** a list of responses to send back to the caller. The list of
responses is "circular" meaning that each response is sent in turn until all have been
sent in which case the first response is sent on the next matching request.

### Imposter builder

To build an imposter the imposter builder is created using the constructor `ImposterBuilder`.
The constructor can be used to initialise the port, protocol and name.

```python
builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
```

#### Adding stubs

Each stub is started by calling `with_stub`, this will return an instance of the class
`StubBuilder`. `StubBuilder` has a fluent interface for building stubs. Stub predicates 
are added using `with_predicate` which can use simple matcher for the path, method, query,
body and headers, (more complex matchers are available). In addition to matching to various
parts of the request there are a number of operators that can be used. The default operator
is 'equals'. Predicates can be combined to make more complex patterns. In the following
example the pattern matches a `POST` to the endpoint path `/api` using the default operator
and combines this with a test that the body `contains` the word `foobar`.
```python
builder.with_stub().with_predicate(method=Method.POST, path='/api').with_predicate(operator='contains', body='foobar')
```

This will respond to a request such as the following
```http request
POST http://localhost:3000/api

{  
    "name": "foobar" 
}
```

For details in the predicates supported by `mountebank` can be found [here](http://www.mbtest.org/docs/api/predicates).

When a stub's predicates match an incoming request it will return a response. Responses are 
added to a stub using the `with_response` method. This method allows you to specify the **body** 
as either text or an object which can be serialised as JSON, the **status code** with the status code number
for the response, **header** are a string/string dictionary of http headers. In addition to specifying what
to return as a response, how the response is returned can also be specified, **wait** can be used to introduce
latency between request and response and **repeat** can be used to specify the number of times the current 
response is repeated. See here a description of other [behaviours](http://www.mbtest.org/docs/api/behaviors).
As an example of a stub, see below:
```python
builder.with_stub().with_predicate(method=Method.POST, path='/api')\
    .with_predicate(operator='contains', body='foobar')\
    .with_response(body={'result': 'Found it!'}, status_code=201).add_stub()
```

This stub will return a JSON object containing the "result".
```http request
POST http://localhost:3000/api

HTTP/1.1 201 Created
Connection: close
Date: Tue, 20 Jun 2023 13:28:07 GMT
Transfer-Encoding: chunked

{
    "result": "Found it!"
}
```

Using behaviours the responses can be dynamic, especially using the **copy** parameter to copy parts of the 
request into the response. The following example is a more complex of the previous but includes an "id" value
taken from the request path and includes it in the "id" feild of the JSON response.
```python
    builder.with_stub().with_predicate(method=Method.POST)\
        .with_predicate(operator='startsWith', path='/api')\
        .with_predicate(operator='contains', body='foobar')\
        .with_response(body={
            'id': '$ID',
            'result': 'Found it!'
    },
        status_code=201,
        copy=Copy(from_="path", into="$ID", using=UsingRegex("\\d+$"))).add_stub()
```

Example calls to this endpoint are as follows:
```http request
POST http://localhost:3000/api/123456

{
    "name": "foobar"
}

HTTP/1.1 201 Created
Connection: close
Date: Tue, 20 Jun 2023 14:19:39 GMT
Transfer-Encoding: chunked

{
    "id": "123456",
    "result": "Found it!"
}
```

```http request
POST http://localhost:3000/api/987654

{
    "name": "Situation",
    "description": "Returned when things go foobar"
}

HTTP/1.1 201 Created
Connection: close
Date: Tue, 20 Jun 2023 14:13:54 GMT
Transfer-Encoding: chunked

{
    "id": "987654",
    "result": "Found it!"
}
```

When there are more than one stub for an imposter, `mountebank` matches them in the order of creation
and responds using the first matching stub (see diagram)[https://freecontent.manning.com/animation-matching-a-request-to-a-response/].
When more than one predicate is required for similar requests, register the most specific patterns before more general 
ones to avoid `mountebank` matching to a more general pattern before checking the more specific.

Having added the stubs the imposter is built by calling the `create` method
```python
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.with_stub().with_predicate(method=Method.GET, path='/test').with_response(body='sausages').add_stub()
    builder.with_stub().with_predicate(method=Method.POST, path='/api')\
        .with_predicate(operator='contains', body='foobar')\
        .with_response(body={'result': 'Found it!'}, status_code=201).add_stub()
    imposter = builder.create()
```

The **copy** behaviour allows for simple substitution of parts of the response with parts from the request.
For much more complex definitions of one or more stubs, or complete imposters there are **templates**.

#### Using templates

Templating is based on (Jinja2)[https://jinja.palletsprojects.com/en/3.1.x/]. From the (documentation)[https://jinja.palletsprojects.com/en/3.1.x/templates/] 
Jinja(2) provides a rich templating language which will allow the creation of complex `mountebank` JSON 
imposter specifications.

Before we use templates to create `mountebank` imposters, it is necessary to understand the format of the JSON
that is used to define them.

```json
{
  "port": 3000,
  "protocol": "http",
  "stubs": [
    {
      "responses": [
        {
          "is": {
            "statusCode": 400
          }
        },
        ...
      ],
      "predicates": [
        {
          "equals": {
            "path": "/test",
            "method": "POST",
            "headers": {
              "Content-Type": "application/json"
            }
          }
        },
        ...
      ]
    },
    ...
  ]
}
```

The definition of an imposter has a **port**, **protocol** and **stubs**. Each stub has **predicates** and **responses**.
Using Jinja templates, this structure can be created programmatically for example:

```json
{
  "port": {{ port }},
  "protocol": "http",
  "stubs": [
          {% for user in users %}
          {
              "predicates": [
                  {
                      "equals": {
                          "path": "/user/{{ user.id }}",
                          "method": "GET"
                      }
                  }
              ],
              "responses": [
                  {
                      "is": {
                          "body": "{\"id\":{{ user.id }},\"name\",:\"{{ user.name }}\",\"'email\":\"{{ user.email }}\"}"
                      }
                  }
              ]
          },
          {% endfor %}
          {
              "predicates":[
                  {
                      "matches": {
                          "path": "/user/.*"
                      }
                  }
              ] ,
              "responses": [
                  {
                      "is": {
                        "statusCode": 404,
                        "body": "{\"errorCode\":\"404 (Not Found)\",\"reason\":\"User with id of $ID not found\"}"
                      },
                      "_behaviors":  {
                          "copy": [
                                {
                                    "from": "path",
                                    "into": "$ID",
                                    "using": {
                                      "method": "regex",
                                      "selector": "\\d+$",
                                      "options": {
                                        "ignoreCase": false,
                                        "multiline": false
                                      }
                                    }
                              }
                          ]
                    }
                  }
                ]
          },
          {
              "predicates": [
                    {
                        "equals": {
                        "path": "/user"
                        }
                    }
              ],
              "responses": [
                  {
                      "is": {
                          "body": "[{% for user in users %}{\"id\":{{ user.id }},\"name\":\"{{ user.name }}\",\"email\":\"{{ user.email }}\"},{% endfor %}]"
                      }
                  }
              ]
          }
  ]
}
```

This template when called with a diction containing the port number and a list of users
will create an imposter listening to the port and has stubs, one for each user at `/user/[user-id]`
,a strub which will match `user/[user-id]` where the id does not match any user so returns a 404 error
at `/user/` will list the users.

The example shows some simple control structures available in Jinja2, many more can be used. 
Templates can be modularised using the `include` tag, and frequently used code can be put into
"macros" which can be accessed using the `import` tag. This should provide enough scope to mock
very complex behaviours.

##### Using templates to create an imposter

To use templates to create an imposter use the `from_template` method on the builder. This method
has two arguments; the first is the template as either a string or as a path to a file containing
the template, the second is a dictionary containing values that are used to substitute placeholders
in the template (`{{ port }}` and users in the example). Various examples can be found in 
`test/imposter_builder_test.py`.

##### Using templates to add stubs

Templates can be used to add stubs to and existing imposter builder using the `from_template`
method on the `StubBuilder` instance. Stubs from a template are appended to the existing list
of stubs. The following example is from `test\imposter_builder_test.py`:

```python
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.with_stub().with_predicate(method=Method.GET, path='/food').with_response(body='sausages').add_stub()
    builder.with_stub().from_template('templates/hello_stubs.json', {'name': name})
    imposter = builder.create()
```

In both cases the location of the templates is relative to the current working directory. If
templates are located elsewhere the path to the root of templates can be set either as an
argument in the constructor or using `templates` property of the imposter builder.

```python
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter",
                              templates="/Users/michael.stewart/PycharmProjects/mountebank-in-action-for-python/test/templates")
```

```python
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.templates = "/Users/michael.stewart/PycharmProjects/mountebank-in-action-for-python/test/templates"
```

The latter maybe useful if templates for stubs are located in separate locations.
