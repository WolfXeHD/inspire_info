import json
import myutils

query = "https://inspirehep.net/api/literature/346986"

data = myutils.read_from_inspire(query)

print(data)


