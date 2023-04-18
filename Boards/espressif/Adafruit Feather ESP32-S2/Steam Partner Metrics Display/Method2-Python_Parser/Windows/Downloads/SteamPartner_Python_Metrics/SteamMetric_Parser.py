import time
import json
import csv

CSV_directory = "/CSV/"  # directory for CSV's just in case
# Set your game app ids in the same order as in the batch script
appID0="xxxxxxx" 
appID1="xxxxxxx" 
appID2="xxxxxxx" 
appID3="xxxxxxx"
appID4="xxxxxxx" 
appID5="xxxxxxx" 
appID6="xxxxxxx" 
appID7="xxxxxxx" 
appID8="xxxxxxx"
appID9="xxxxxxx"
appID10="xxxxxxx" 

PATH0 = "SteamWishlists_GameAppID0_all.csv"
PATH1 = 'SteamWishlists_GameAppID1_all.csv'
PATH2 = 'SteamWishlists_GameAppID2_all.csv'
PATH3 = 'SteamWishlists_GameAppID3_all.csv'
PATH4 = 'SteamWishlists_GameAppID4_all.csv'
PATH5 = 'SteamWishlists_GameAppID5_all.csv'
PATH6 = 'SteamWishlists_GameAppID6_all.csv'
PATH7 = 'SteamWishlists_GameAppID7_all.csv'
PATH8 = 'SteamWishlists_GameAppID8_all.csv'
PATH9 = 'SteamWishlists_GameAppID9_all.csv'
PATH10 = 'SteamWishlists_GameAppID9_all.csv'
#print ("\nFile Path : ", PATH0)

sums0 = 0
sums1 = 0
sums2 = 0
sums3 = 0
sums4 = 0
sums5 = 0
sums6 = 0
sums7 = 0
sums8 = 0
sums9 = 0
sums10 = 0
with open(PATH0) as csvfile0:
    sep = ","
    while (line := csvfile0.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile0, delimiter=sep):
        try:
            sums0 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID0 Total Adds: ", sums0)
  
with open(PATH1) as csvfile1:
    sep = ","
    while (line := csvfile1.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile1, delimiter=sep):
        try:
            sums1 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID1 Total Adds: ", sums1)

with open(PATH2) as csvfile2:
    sep = ","
    while (line := csvfile2.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile2, delimiter=sep):
        try:
            sums2 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID2 Total Adds: ", sums2)
 
with open(PATH3) as csvfile3:
    sep = ","
    while (line := csvfile3.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile3, delimiter=sep):
        try:
            sums3 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID3 Total Adds: ", sums3)

with open(PATH4) as csvfile4:
    sep = ","
    while (line := csvfile4.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile4, delimiter=sep):
        try:
            sums4 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID4 Total Adds: ", sums4)
   
with open(PATH5) as csvfile5:
    sep = ","
    while (line := csvfile5.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile5, delimiter=sep):
        try:
            sums5 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID5 Total Adds: ", sums5)
  
with open(PATH6) as csvfile6:
    sep = ","
    while (line := csvfile6.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile6, delimiter=sep):
        try:
            sums6 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID6 Total Adds: ", sums6)
  
with open(PATH7) as csvfile7:
    sep = ","
    while (line := csvfile7.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile7, delimiter=sep):
        try:
            sums7 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID7 Total Adds: ", sums7)

with open(PATH8) as csvfile8:
    sep = ","
    while (line := csvfile8.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile8, delimiter=sep):
        try:
            sums8 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID8 Total Adds: ", sums8)

with open(PATH9) as csvfile9:
    sep = ","
    while (line := csvfile9.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile9, delimiter=sep):
        try:
            sums9 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID9 Total Adds: ", sums9)

with open(PATH10) as csvfile10:
    sep = ","
    while (line := csvfile10.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile10, delimiter=sep):
        try:
            sums9 += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("appID10 Total Adds: ", sums10)

# Data to be written
dictionary = {
    "Game0": (sums0),
    "Game1": (sums1),
    "Game2": (sums2),
    "Game3": (sums3),
    "Game4": (sums4),
    "Game5": (sums5),
    "Game6": (sums6),
    "Game7": (sums7),
    "Game8": (sums8),
    "Game9": (sums9),
    "Game10": (sums10),
}

json_object = json.dumps(dictionary, indent=4)
with open("Wishlists.json", "w") as outfile:
    outfile.write(json_object)