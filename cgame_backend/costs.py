from inventory import Inventory


class ResourceList:
    def __init__(self, d):
        self.d = d


class Costs:
    def __init__(self):
        self.costs = {}

    def addCosts(self, name: str, costs: ResourceList):
        self.costs[name] = costs

    def addStandardCosts(self):
        self.addCosts("street", ResourceList({"wood": 1, "clay": 1}))
        self.addCosts("settlement", ResourceList({"wood": 1, "clay": 1, "wheat": 1, "sheep": 1}))
        self.addCosts("city", ResourceList({"ore": 3, "wheat": 2}))
        self.addCosts("development", ResourceList({"wheat": 1, "sheep": 1, "ore": 1}))

    def affordable(self, inventory: Inventory, name: str):
        if name in self.costs:
            resources = self.costs[name].d
            for item in resources:
                if inventory.get(item) < resources[item]:
                    return False
            return True
        return False

    def afford(self, inventory: Inventory, name: str):
        if name in self.costs:
            resources = self.costs[name].d
            for item in resources:
                inventory.add(item, -resources[item])

    def give(self, inventory: Inventory, name: str):
        if name in self.costs:
            resources = self.costs[name].d
            for item in resources:
                inventory.add(item, resources[item])
