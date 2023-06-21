from mbtest.server import MountebankServer
from imposter_builder import ImposterBuilder, Protocol, Method, Copy, UsingRegex

from json import dumps

def main():
    users = [{'id': f'{i}', 'name': f'Tester_{i}', 'email': f'tester{i}@testing.com'} for i in range(1, 6)]

    server = MountebankServer(port=2525, host='127.0.0.1')
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.with_stub().with_predicate(method=Method.GET, path='/test').with_response(body='sausages').add_stub()
    builder.with_stub().with_predicate(method=Method.POST)\
        .with_predicate(operator='startsWith', path='/api')\
        .with_predicate(operator='contains', body='foobar')\
        .with_response(body={
            'id': '$ID',
            'result': 'Found it!'
    },
        status_code=201,
        copy=Copy(from_="path", into="$ID", using=UsingRegex("\\d+$"))).add_stub()
    builder.with_stub().from_template('templates/users.json', {'users': users})
    imposter = builder.create()
    with server(imposter) as ms:
        print(ms.query_all_imposters())
        input('Press return when testing is complete.')


if __name__ == '__main__':
    main()