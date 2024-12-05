# DegreesOfSpotify
Welcome to Degrees of Spotify

Created By: Laurynas Kanopka, Jordan Price, Ale De-La-O

This project takes in two artists as inputs, and by either using depth first search or breadth first search, it will return a path between the two artists through artists that they have have features in common with.

BFS will return the shortest path
Because of the nature of DFS, to find the shortest path, it would need to explore every route to find the shortest one, and with the size of the Spotify Database, that's not really possible in our scope

How to run the code:
1. Run the SpotipyGUI.py program, which will open up the GUI
2. Type the artist you want to start with in the box next to "Artist 1" and click the "Confirm" button
3. Type the artist you want to end with in the box next to "Artist 2" and click the "Confirm" button
4. Select which search alrorithm you want to use with the buttons next to "Select Search Algorithm:"
5. Click the "DFS" button for Depth-First Search or click the "BFS" button for Breadth-First Search
6. Click the "Search" button next to "Find Degrees of Separation:" to begin the search
7. The degrees of separation will be displayed next to "Degree of Separation:"
8. The path between the artists will be displayed on the next row down, starting with Artist 1 and ending with Artist 2
9. The final row will then display the number of artists that were searched to get to the result
