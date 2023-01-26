from imposter_builder import ImposterBuilder, Protocol


def create_inventory_imposter():
    return ImposterBuilder(port=3000, protocol=Protocol.HTTPS, name="Inventory Service")\
        .from_template('configfiles', 'inventory.json')\
        .create()
