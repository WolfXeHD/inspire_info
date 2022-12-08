import glob

files = glob.glob("bibtex/*")

total_data = ""
for file in files:
    with open(file, "r") as f:
        data = f.read()
    total_data += "\n\n"
    total_data += data

with open("total_publications.tex", "w") as f:
    f.write(total_data)

