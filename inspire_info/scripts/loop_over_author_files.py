__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import glob
import inspire_info


files = glob.glob("authors/*.txt")
for file in files:
    bais_to_check = inspire_info.myutils.get_inspire_bai(file)
    for bai in bais_to_check:
        query = inspire_info.build_person_query(bai, search_type='literature')
        data = inspire_info.read_from_inspire(query, silent=True)
