@echo off
set mydate=%date:~10,4%-%date:~4,2%-%date:~7,2%

rem Set your game app id CSVs to be downloaded
set appID0=xxxxxxx
set appID1=xxxxxxx
set appID2=xxxxxxx
set appID3=xxxxxxx
set appID4=xxxxxxx
set appID5=xxxxxxx
set appID6=xxxxxxx
set appID7=xxxxxxx
set appID8=xxxxxxx
set appID9=xxxxxxx
set appID9=xxxxxxx

Rem Configure these paths
set CircuitPythonDrive=I:\
set PythonScriptPath=C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamMetric_Parser.py

echo --------------------------------------
echo Date: %mydate%
echo Steam Partner CSV Metrics Updater
echo Edge and this window will automatically close when done
echo --------------------------------------

Rem This is just MSEdge launching a new download tab per game title CSV. All urls are the same except for the appID
Rem A user on the PC must be logged into Steam on MSEdge, have auto downloads set to /downloads folder, and have access to Partner Reports for the download to work.
start "" msedge.exe --restore-last-session --window-size="800,600" https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID0%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID0%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID1%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID1%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID2%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID2%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID3%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID3%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID4%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID4%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID5%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID5%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID6%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID6%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID7%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID7%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID8%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID8%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID9%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID9%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID10%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID10%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter

timeout /T 6
taskkill /IM msedge.exe /F 
echo.
echo Moving downloaded CSV to SteamPartner_Metrics Directory

move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID0%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID0_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID1%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID1_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID2%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID2_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID3%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID3_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID4%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID4_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID5%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID5_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID6%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID6_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID7%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID7_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID8%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID8_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID9%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID9_all.csv
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID10%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\SteamWishlists_GameAppID10_all.csv

echo Deleting %USERNAME%\Downloads\SteamWishlists_*.csv 
del C:\Users\%USERNAME%\Downloads\SteamWishlists_*.csv
echo.
echo Parsing all CSV Files with Python...
start "" python %PythonScriptPath%
echo.
echo Attempting to create and copy Wishlist.json to Circuit Python Device on Flash Drive %CircuitPythonDrive%
timeout /T 2
copy C:\Users\%USERNAME%\Downloads\SteamPartner_Python_Metrics\Wishlists.json %CircuitPythonDrive%\JSON\Wishlists.json
exit