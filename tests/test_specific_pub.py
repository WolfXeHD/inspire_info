import inspire_info

query = "https://inspirehep.net/api/literature?sort=mostrecent&size=500&page=1&q=author%20Kher%20Sham%20Lim&ui-citation-summary=true&ui-exclude-self-citations=true"

data = inspire_info.read_from_inspire(query)

for publication in data["hits"]["hits"]:
    pub = inspire_info.Publication(publication)
    print(pub.title)
    print(pub.keywords)
    print(pub.id)
