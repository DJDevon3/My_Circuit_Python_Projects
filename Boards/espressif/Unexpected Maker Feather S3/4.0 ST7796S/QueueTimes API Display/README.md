### Queue-Times.com API on TFT Display
- Pulls API data info a buffer for offline use and immediately disconnects
- Reconnects only to update the buffer with new JSON data

### Stored JSON data loops infinitely until time to reconnect
- Shows Land (area the attraction/ride is in)
- Shows Name of the attraction/ride
- Shows queue time for the attraction/ride
- Show Status if the attraction/ride is currently Open/Closed


https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/59248691-cf3c-49de-98f2-35325a2fc8dc

Serial output example:
```
===============================
Connecting to WiFi...
✅ WiFi!
 | Attempting to GET Queue-Times JSON!
 | ✅ Queue-Times JSON!
✂️ Disconnected from Queue-Times API

Finished!
Board Uptime: 3 hours
Next Update: 5 minutes
===============================
 |  | Lands: Adventureland
 |  | Rides: Adventureland Treehouse inspired by Walt Disney’s Swiss Family Robinson
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Indiana Jones™ Adventure
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Jungle Cruise
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Walt Disney's Enchanted Tiki Room
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Lands: Critter Country
 |  | Rides: Davy Crockett's Explorer Canoes
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Splash Mountain
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: The Many Adventures of Winnie the Pooh
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Lands: Fantasyland
 |  | Rides: "it's a small world"
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Alice in Wonderland
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Casey Jr. Circus Train
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Dumbo the Flying Elephant
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: King Arthur Carrousel
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Mad Tea Party
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Matterhorn Bobsleds
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Meet Tinker Bell in Pixie Hollow
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Mr. Toad's Wild Ride
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Peter Pan's Flight
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Pinocchio's Daring Journey
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Snow White's Enchanted Wish
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Storybook Land Canal Boats
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Lands: Frontierland
 |  | Rides: Big Thunder Mountain Railroad
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Mark Twain Riverboat
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Pirate's Lair on Tom Sawyer Island
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Sailing Ship Columbia
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Lands: Main Street U.S.A
 |  | Rides: The Disneyland Story presenting Great Moments with Mr. Lincoln
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Lands: Mickey's Toontown
 |  | Rides: Chip 'n' Dale's GADGETcoaster
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Goofy's How-to-Play Yard
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Mickey & Minnie's Runaway Railway
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Mickey's House and Meet Mickey Mouse
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Roger Rabbit's Car Toon Spin
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Lands: New Orleans Square
 |  | Rides: Pirates of the Caribbean
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Lands: Star Wars: Galaxy's Edge
 |  | Rides: Millennium Falcon: Smugglers Run
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Millennium Falcon: Smugglers Run Single Rider
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Star Wars: Rise of the Resistance
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Lands: Tomorrowland
 |  | Rides: Autopia
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Buzz Lightyear Astro Blasters
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Disneyland Monorail
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Finding Nemo Submarine Voyage
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Space Mountain
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
 |  | Rides: Star Tours - The Adventures Continue
 |  | Queue Time: 0 Minutes
 |  | Status: Closed
```
This cycle will repeat infinitely until it's time to reconnect to the API and get new data.

