## Examples: using mountebank running in container.

This example show the configuration of a simple imposter using `mountebank` 
running within a container. The example can be run without a running container
but the primary purpose of the example is to show it with one running.

### Starting ` mountebank` container

#### Command line

The following commandline will start a container suitable for this example
`docker run -p 2525:2525 -p 3000:3000 --name mountebank bbyars/mountebank:latest`

This will map the mountebank port 2525, to the same port on the host, the imposter 
port 3000 is similarly mapped to the same port on the host.

#### Using Jetbrains IDE

1. In Services tab, connect to Docker (assuming it is running)
2. Open Docker node
3. Right-click Images node
   3.1 Select "Pull image..."
   3.2 Enter `bbyars/mountebank` in "Image to pull:"
4. Once the image has been pulled
   4.1 Right-click on `bbyars/mountebank:latest` node
   4.2 Click on "Create Container" or click on "Create Container" button
   4.3 Enter a Name and Container Name
   4.4 Click on "Modify options" and select "Bind ports -p"
   4.5 Click on folder icon.
   4.6 Click on + button enter 2525 in both "Host port" and "Container port"
   4.7 Repeat for port 3000
   4.8 Start container by clicking on "Run"

When the container is running a message similar to

```
mountebank v2.8.2 now taking orders - point your browser to http://localhost:2525/ for help
```

should be displayed.

### Using `Examples.py` to add imposters

#### From commandline

Use the following:
```shell
 export PYTHONPATH=/[path]/[to]/[project-folder]/
 python examples.py
```

The following will be displayed:
```text
[mbtest.imposters.imposters.Imposter(stubs=[mbtest.imposters.stubs.Stub(predicates=[mbtest.imposters.predicates.Predicate(path='/test', method=<Method.GET: 'GET'>, query=None, body=None, headers=None, xpath=None, operator=<Operator.EQUALS: 'equals'>, case_sensitive=True)], responses=[mbtest.imposters.responses.Response(http_response=mbtest.imposters.responses.HttpResponse(_body='sausages', status_code=200, headers=None, mode=<Mode.TEXT: 'text'>), wait=None, repeat=None, copy=None, decorate=None, lookup=None, shell_transform=None)])], port=3000, protocol=<Protocol.HTTP: 'http'>, name='MyImposter', default_response=None, record_requests=True, host='127.0.0.1', server_url=furl('http://127.0.0.1:2525/imposters'), mutual_auth=False, key=None, cert=None)]
Press return when testing is complete. 
```
Enter the URL: `http://localhost:3000/test` in your browser and this should respond with `sausages`.

#### Using Jetbrains

Open the `examples.py` file in the window, close to the end of the file there is a green arrow. 
Click this to start the script.

To test open the file `examples.http`, click arrow next to `http://localhost:2525/imposters` to see the imposters
defined in `mountebank`. To test the imposter defined click the arrow next to `http://localhost:3000/test`
