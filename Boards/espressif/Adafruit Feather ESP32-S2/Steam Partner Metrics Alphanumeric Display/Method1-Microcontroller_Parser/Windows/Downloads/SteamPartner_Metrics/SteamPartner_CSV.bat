@echo off
set mydate=%date:~10,4%-%date:~4,2%-%date:~7,2%
Rem set your Game ID here
set appID=xxxxxxx

start "" msedge.exe --restore-last-session --window-size="800,600" https://partner.steampowered.com/report_csv.php?file=SteamWishlists_%appID%_2018-01-25_to_%mydate%^&params=query=QueryWishlistActionsForCSV^^appID=%appID%^^dateStart=2018-01-25^^dateEnd=%mydate%^^interpreter=WishlistReportInterpreter
echo --------------------------------------
echo Steam Partner CSV Metrics Updater
echo Edge and this window will automatically close when done
echo --------------------------------------
timeout /T 5
taskkill /IM msedge.exe /F 
echo.
echo File Date: %mydate%
echo Moving downloaded CSV to SteamPartner_Metrics Directory
move C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID%_2018-01-25_to_%mydate%.csv C:\Users\%USERNAME%\Downloads\SteamPartner_Metrics\SteamWishlists_GameAppID_all.csv
echo Deleting CSV in %USERNAME%\Downloads Directory
del C:\Users\%USERNAME%\Downloads\SteamWishlists_%appID%_2018-01-25_to_*.csv
echo Copying CSV to Circuit Python Device on Flash Drive H:\
timeout 2
copy C:\Users\%USERNAME%\Downloads\SteamPartner_Metrics\SteamWishlists_GameAppID_all.csv H:\CSV\SteamWishlists_GameAppID_all.csv