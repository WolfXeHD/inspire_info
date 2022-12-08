import glob
import inspire_info



files = glob.glob("authors/*.txt")
files = ["authors/author_Hoetzsch, Luisa.txt"]
for file in files:
    bais_to_check = inspire_info.myutils.get_inspire_bai(file)
    for bai in bais_to_check:
        query = inspire_info.build_person_query(bai, search_type='literature')
        data = inspire_info.read_from_inspire(query, silent=True)
