from imposter_builder import ImposterBuilder, Protocol

product_port = 3000
content_port = 4000


def create_product_imposter():
    return ImposterBuilder(port=product_port, protocol=Protocol.HTTP,
                           name='Product Service').with_stub().with_predicate(path='/products').with_response(
                           status_code=200, headers={"Content-Type": "application/json"},
                           body={"products": [
                                {
                                    "id": "2599b7f4",
                                    "name": "The Midas Dogbowl",
                                    "description": "Pure gold"
                                },
                                {
                                    "id": "e1977c9e",
                                    "name": "Fishtank Amore",
                                    "description": "Show your fish some love"
                                }]}).add_stub().create()


def create_content_imposter():
    return ImposterBuilder(port=content_port, protocol=Protocol.HTTP,
                           name='Content Service').with_stub().with_predicate(
                           path='/content', query={"ids": "2599b7f4,e1977c9e"}).with_response(
                           status_code=200, headers={"Content-Type": "application/json"},
                           body={"content": [{"id": "2599b7f4",
                                               "copy": "Treat your dog like the king he is",
                                               "image": "/content/c5b221e2"},
                                              {"id": "e1977c9e",
                                               "copy": "Love your fish; they'll love you back",
                                               "image": "/content/a0fad9fb"}]}).add_stub().create()
