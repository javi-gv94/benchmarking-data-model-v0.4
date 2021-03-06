import os
import io, json
import pandas
import id_generator

def run(cancer_types, long_names, mongo_ids, tool_contact, download_urls, out_dir):

    last_challenge = "0000000"
    last_participant_dataset = "0000000"
    last_tool = "0000008"

    IDGenerator = id_generator.IDGenerator()

    for cancer in cancer_types:

        challenge_id, last_challenge = IDGenerator.get_new_OEB_id("002", "X", last_challenge)

        for participant in os.listdir("/home/jgarrayo/PycharmProjects/TCGA_benchmark/input/participants"):

            # if participant is not in mongo, assign new temporary id
            if participant in mongo_ids:
                tool_id = mongo_ids[participant]
            else:
                tool_id, last_tool = IDGenerator.get_new_OEB_id("002", "T", last_tool)

            # get participant dataset id
            participant_data_id, last_participant_dataset = IDGenerator.get_new_OEB_id("002", "D", last_participant_dataset)

            info = {
                "_id": "TCGA:2018-04-05_" + cancer + "_P_" + participant,
                "name":"Cancer Driver Genes in " + long_names[cancer],
                "description":"List of Cancer Driver Genes predicted by tool " + participant + " in " + long_names[cancer],
                "dates":{
                   "creation":"2018-04-05T00:00:00Z",
                   "modification":"2018-04-05T14:00:00Z"
                },
                "datalink": {
                    "uri": download_urls[participant],
                    "attrs": ["archive"],
                    "validation_date": "2018-04-05T00:00:00Z",
                    "status": "ok"
                },
                "type":"participant",
                "visibility": "public",
                "_schema":"https://www.elixir-europe.org/excelerate/WP2/json-schemas/1.0/Dataset",
                "community_ids":["OEBC001"],
                "challenge_ids": ["TCGA:2018-04-05_" + cancer],
                "depends_on":{
                   "tool_id":"TCGA:" + participant,
                   "rel_dataset_ids":[
                      {
                         "dataset_id": "TCGA:2018-04-05_input",
                      }
                   ]
                },
                "version":"unknown",
                "dataset_contact_ids":[
                   tool_contact[participant]
                ]
            }

            # print info
            filename = "Dataset_participant_" + cancer + "_" + participant + "_" + participant_data_id + ".json"
            # print filename

            with open(out_dir + filename, 'w') as f:
                json.dump(info, f, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":


    cancer_types = ["ACC", "BLCA", "BRCA", "CESC", "CHOL", "COAD", "DLBC", "ESCA", "GBM", "HNSC", "KICH", "KIRC",
                    "KIRP", "LAML", "LGG", "LIHC", "LUAD", "LUSC", "MESO", "OV", "PAAD", "PCPG", "PRAD",
                    "READ", "SARC", "SKCM", "STAD", "TGCT", "THCA", "THYM", "UCEC", "UCS", "UVM", "ALL"]

    data = pandas.read_csv("../cancer_names.tsv", sep="\t",
                           comment="#", header=None)

    long_names = {}
    for index, row in data.iterrows():
        long_names[row[0]] = row[1]

    # read file which containes tool ids already pushed to mongo
    with io.open("../mongo_tools_ids.txt", mode='r', encoding="utf-8") as f:
        mongo_ids = json.load(f)

    # read file which containes tool contact
    with io.open("../tools_contacts.txt", mode='r', encoding="utf-8") as f:
        tool_contact = json.load(f)

    # read file which contains download links with participant predictions
    with io.open("../participant_data_urls.txt", mode='r', encoding="utf-8") as f:
        download_urls = json.load(f)

    # Assuring the output directory does exist
    out_dir = "out/participant_datasets/"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    run(cancer_types, long_names, mongo_ids, tool_contact, download_urls,out_dir)