# Simple Russian BlackJack

### Idea:
While vacationing in another country without a laptop, I wanted to write a simple card game using only my phone.


### Progress:
I wrote this code lying on a longer near the pool. In total, it took 1.5-2 hours. This code doesnt much sense, i just wanted to write :)

### Rules of game:
This is a realization of the game blackjack, which in Russia is called 21 points. The goal is to get 21 points, or as close to this value as possible. If you get more - you lose, if you get less than 21 and less than your opponent - you lose, if both get more than 21 one - it's a draw. 36 cards are used, cards with a value of 6 to 10 mean the same as what is written on them, the king is equal to 4, the queen is equal to 3, the jack is equal to 2. An ace is equal to 11, but if you have only two aces - an automatic win.

### Additional
To test some functions I have introduced debug commands that can be considered as cheats. If you want to play fair - just don't use them.

- ```&ingame_cards``` - Displays the cards remaining in the deck.
- ```&get_money_{count}``` - Get money to player
- ```&rm_cards``` - Remove all cards from deck, leaving only cards on hand
- ```&bot_cards``` - Displays bot's cards

### Technical info
- Developer: Urban Egor
- Version: 4.4.25 r

I used an OOP principles in this project (lol), like a practice. I implemented realistic deck with uniq cards and and the property of ending, bot player with difficulty setup and action selection based on situational analysis and probabilities, and bot doesnt see player cards what makes him a fair opponent. 

For writing this project i using Pro version of PyDroid. 


### How to play?
1. ```git clone https://github.com/Egor-Urban/SimpleRussianBlackJack.git```
2. ```cd /SimpleRussianBlackJack```
3. ```python game.py```

U can play on any device where you can run python programs
