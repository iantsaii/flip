# Flip
#### Video Demo:  <URL HERE>
#### Description:


##### What does the project do?

The app allows a group of friends to randomly decide who’s going to pay for a bill. Each friend would create an account, then they would create groups by adding their friends’ accounts. Whenever they want to settle a bill, they can press the ‘flip’ button of their group. The website will randomly decide who will pay for the bill, and log the result into a table for the users to see.

I had heard about this unique company culture where employees split the bill for a team meal by flipping a coin to decide who would foot the entire bill. People would only play this game with someone that they would continue spending more money with. So agreeing to settle a bill like this signals expectation of a long-lasting friendship and incentivises them to spend more money together, hence fostering connections between friends.

However, due to pure chance, someone may pay the bill too many times in a row. When that happens, he may become anxious about losing money to his friends, when in reality he had already benefited multiple times from his friends paying his bill.

If each friend could see the entire history of every single time they had paid for each other’s bills and see how much each of them had contributed, nobody would feel like they are losing out, making it easier for them to continue using this method of settling bills.

A side benefit of this practice is that it saves the hassle of getting everyone to pay up for their own share of the bill.


##### What do each of the files contain and do?
The application.py file contains functions that will be called when the client makes HTTP requests clicking on a link or button on the website. It uses data from the flip.db file which  contains data about all users, groups, group membership and transactions in each table. The helpers.py file contains functions and decorators that will be used frequently in application.py. The requirements.txt file includes a list of required libraries for our application. The templates folder contains the HTML files that the user will see.

The home page displays a list of all the groups a user belongs to. Beside each group name, there is a button which will take users to the 'transactions' page showing them the history of the group's transactions.

At the transactions page, users can provide a transaction name, and an amount of money to be settled, and then click a 'Flip' button to randomly decide who's going to pay that sum of money. When the user clicks the 'Flip' button, the client submits a request to the server for '/flip'. The function at the 'flip' route will generate a random number corresponding to the group member that will pay for the bill. Afterwards, a string of text will appear on the same page that determines who will be paying how much money for what expense. On the same page, users can also see how much each member of the group has paid since the group's creation.

Users can click on the 'New Group' link at the navigation bar that will take them to the 'create' page. Here, they can add in the usernames of their friends and click 'Create Group' to create the group

If an error occurs, the apology page will display the error code along with a relevant message.


##### What design choices did you make? Why?

At first, I considered making a feature where people could randomly decide who’s going to pay the bills without even creating an account. However, I realised this did not address the insecurity that users felt when using this method of settling bills, so I scrapped the idea. Besides, people could easily use other random number generators to decide.
