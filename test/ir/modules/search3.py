# Imports

from core import getES, config, configs


# Config

config = config(
    page_size = "10"
)


# Functions

def execute(receive):
    # Include the keywords in a query object (JSON)
    query = {
        "from": receive.start,
        "size": configs.search3.page_size,
        "query": {
            "multi_match": {
                "query": receive.keywords,
                "fields": [
                    "Title^3",
                    "Description",
                    "Tags^2"
                ]
            }
        },
        "sort": {
            "_score": {
                "order": "desc"
            },
            "Downloads": {
                "order": "desc"
            },
            "Views": {
                "order": "desc"
            }
        }
    }

    # Send a search request with the query to server
    res = getES().search(index = "wbliu20_team_project", body = query)
    hits = res["hits"]
    return hits