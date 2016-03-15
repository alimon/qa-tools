from testopia_update.product import Product

class ToasterProduct(Product):
    name = 'Toaster'
    results_regex = "^.*RESULTS.*test_(?P<case_id>\d+): (?P<status>PASSED|FAILED)$"
