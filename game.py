# Simple Russian Blackjack in terminal
# Version: 4.4.25 r
# Developer: Urban Egor


import random
import os
import time



RANKS = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
VALUES = {'6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 2, 'Q': 3, 'K': 4, 'A': 11}
DIFFICULTY_THRESHOLDS = {'easy': 0.2, 'normal': 0.35, 'hard': 0.5}
BET_RANGES = {'easy': (5, 15), 'normal': (10, 30), 'hard': (20, 50)}



class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = VALUES[rank]


    def __str__(self):
        return f"{self.rank}{self.suit}"


    def __hash__(self):
        return hash((self.rank, self.suit))


    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit



class Deck:
    def __init__(self):
        self.used_cards = set()
        self.refresh()


    def refresh(self):
        self.cards = [
            Card(rank, suit)
            for rank in RANKS
            for suit in SUITS
            if Card(rank, suit) not in self.used_cards
        ]
        random.shuffle(self.cards)


    def draw(self):
        if not self.cards:
            raise RuntimeError("Cards is end.")
        card = self.cards.pop()
        self.used_cards.add(card)
        return card


    def remove_except(self, keep_cards):
        keep_set = set(keep_cards)
        self.used_cards = keep_set.copy()
        self.cards = [card for card in self.cards if card in keep_set]



class Hand:
    def __init__(self):
        self.cards = []


    def add(self, card):
        self.cards.append(card)


    def get_score(self):
        return sum(card.value for card in self.cards)


    def is_bust(self):
        return self.get_score() > 21


    def show(self, hidden=False):
        if hidden and self.cards:
            return "[??] " + " ".join(str(card) for card in self.cards[1:])
        return " ".join(str(card) for card in self.cards)



class Player:
    def __init__(self, name, coins=100):
        self.name = name
        self.hand = Hand()
        self.coins = coins
        self.wins = 0
        self.losses = 0


    def reset_hand(self):
        self.hand = Hand()


    def add_card(self, card):
        self.hand.add(card)


    def is_bust(self):
        return self.hand.is_bust()


    def score(self):
        return self.hand.get_score()


    def can_bet(self, amount):
        return self.coins >= amount



class HumanPlayer(Player):
    def take_turn(self, deck, game=None):
        while True:
            print(f"\nYou cards is: {self.hand.show()}  | Score: {self.score()}")
            if self.is_bust():
                print("Too many! You bust!")
                break
            choice = input("Take card? [y/n or &cmd]: ").strip().lower()
            if choice.startswith("&") and game:
                game.debug_command(choice)
                continue
            if choice in ('д', 'y'):
                try:
                    self.add_card(deck.draw())
                except RuntimeError:
                    raise
            elif choice in ('н', 'n'):
                break



class BotPlayer(Player):
    def __init__(self, name, difficulty='normal', coins=100):
        super().__init__(name, coins)
        self.difficulty = difficulty


    def take_turn(self, deck, game=None):
        while True:
            score = self.score()
            remaining = deck.cards
            safe = [card for card in remaining if self._would_not_bust(score, card)]
            prob = len(safe) / len(remaining) if remaining else 0
            threshold = DIFFICULTY_THRESHOLDS[self.difficulty]
            if score < 17 and prob > threshold:
                try:
                    self.add_card(deck.draw())
                except RuntimeError:
                    raise
                time.sleep(1)
            else:
                break


    def _would_not_bust(self, score, card):
        value = 1 if card.rank == 'A' and score + 1 <= 21 else card.value
        return score + value <= 21

    def choose_bet(self, opponent_coins):
        min_bet, max_bet = BET_RANGES[self.difficulty]
        bet = random.randint(min_bet, max_bet)
        return min(bet, self.coins, opponent_coins)



class Game:
    def __init__(self):
        self.difficulty = 'normal'
        self.human = HumanPlayer("Player")
        self.bot = BotPlayer("Bot", difficulty=self.difficulty)
        self.deck = Deck()
        self.bet = 0


    def main_menu(self):
        while True:
            self.clear_screen()
            print("===== 21 Score =====")
            print(f"Coins: Player — {self.human.coins}, Bot — {self.bot.coins}")
            print(f"Wins: {self.human.wins} | Loss: {self.human.losses}")
            print("1 - Start Game")
            print("2 - Setup Bot (now level: {})".format(self.bot.difficulty))
            print("3 - Exit")

            choice = input("Choose: ").strip()

            if choice.startswith('&'):
                self.debug_command(choice, context='menu')
                continue

            if choice == '1':
                self.play()
            elif choice == '2':
                self.configure_bot()
            elif choice == '3':
                break


    def configure_bot(self):
        self.clear_screen()
        print("You choose bot hardness:")
        print("1 - Easy like cake")
        print("2 - Medium (normal)")
        print("3 - Hardest like brick")
        choice = input("Choose: ").strip()
        mapping = {'1': 'easy', '2': 'normal', '3': 'hard'}
        self.difficulty = mapping.get(choice, 'normal')
        self.bot = BotPlayer("Bot", difficulty=self.difficulty, coins=self.bot.coins)


    def play(self):
        if self.human.coins == 0:
            print("You no coins. Game is over.")
            input("Press Enter...")
            return
        if self.bot.coins == 0:
            print("Bot is out of money. You big win!")
            input("Press Enter...")
            return

        self.human.reset_hand()
        self.bot.reset_hand()

        try:
            for _ in range(2):
                self.human.add_card(self.deck.draw())
                self.bot.add_card(self.deck.draw())
        except RuntimeError:
            self.handle_deck_exhaustion()
            return

        first = random.choice([self.human, self.bot])
        second = self.bot if first == self.human else self.human

        self.clear_screen()
        print("===== New Round Start =====")
        print(f"{self.human.name}: {self.human.coins} coins")
        print(f"{self.bot.name}: {self.bot.coins} coins")
        print(f"\nFirst move: {first.name}")

        self.bet = self.make_bet(first, second)
        if self.bet == 0:
            print("Bet not good. Skip round.")
            input("Press Enter...")
            return

        try:
            first.take_turn(self.deck, self if isinstance(first, HumanPlayer) else None)
            self.clear_screen()
            second.take_turn(self.deck, self if isinstance(second, HumanPlayer) else None)
        except RuntimeError:
            print("\n❌ Game broken: deck is over.")
            self.handle_deck_exhaustion()
            return

        self.resolve()


    def make_bet(self, initiator, opponent):
        if isinstance(initiator, BotPlayer):
            bet = initiator.choose_bet(opponent.coins)
            print(f"Bot bet is {bet} coins.")
            input("Press Enter...")
            return bet
        while True:
            print(f"\nHow many coins bet? (you: {initiator.coins}, opponent: {opponent.coins})")
            try:
                bet = int(input("Bet: ").strip())
                if 1 <= bet <= min(initiator.coins, opponent.coins):
                    return bet
            except:
                pass
            print("Bet bad. Try again.")


    def resolve(self):
        h_score = self.human.score()
        b_score = self.bot.score()

        print("\n--- Result Time ---")
        print(f"You cards: {self.human.hand.show()} | Score: {h_score}")
        print(f"Bot cards: {self.bot.hand.show()} | Score: {b_score}")

        result = self.determine_winner(h_score, b_score)
        print(f"\nResult: {result}")

        if "win" in result:
            self.human.coins += self.bet
            self.bot.coins -= self.bet
            self.human.wins += 1
            self.bot.losses += 1
        elif "lose" in result:
            self.human.coins -= self.bet
            self.bot.coins += self.bet
            self.human.losses += 1
            self.bot.wins += 1

        print(f"\nCoins: Player — {self.human.coins}, Bot — {self.bot.coins}")
        print(f"Score: Win — {self.human.wins}, Lose — {self.human.losses}")
        input("\nPress Enter for next...")


    def handle_deck_exhaustion(self):
        h_score = self.human.score()
        b_score = self.bot.score()

        print("\n--- Deck is dead ---")
        print(f"You cards: {self.human.hand.show()} | Score: {h_score}")
        print(f"Bot cards: {self.bot.hand.show()} | Score: {b_score}")

        if not self.human.hand.cards or not self.bot.hand.cards:
            print("Not enough card. Is draw.")
        elif len(self.bot.hand.cards) < 2 or len(self.human.hand.cards) < 2:
            print("Someone not get enough cards. Is draw.")
        else:
            self.resolve()


    def determine_winner(self, h, b):
        if h > 21 and b > 21:
            return "Both bust. Draw."
        if h > 21:
            return "You lose. Too much."
        if b > 21:
            return "You win! Bot bust!"
        if h > b:
            return "You win!"
        if b > h:
            return "You lose."
        return "Draw."


    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")


    def debug_command(self, command, context='game'):
        allowed_in_menu = {'&ingame_cards', '&rm_cards'}
        if command.startswith('&get_money_'):
            if context in ('menu', 'game'):
                try:
                    amount = int(command.split('_')[-1])
                    self.human.coins += amount
                    print(f"{amount} coins added.")
                except:
                    print("Bad format.")
                input("Press Enter...")
                return
        if context == 'menu' and command not in allowed_in_menu:
            print("Command not can use in menu.")
            input("Press Enter...")
            return

        if command == '&ingame_cards':
            print("\nLeft in deck:")
            print(" ".join(str(c) for c in self.deck.cards) or "Deck empty")
            input("Press Enter...")

        elif command == '&rm_cards':
            keep = self.human.hand.cards + self.bot.hand.cards
            self.deck.remove_except(keep)
            print("Deck clean. Only game cards now.")
            input("Press Enter...")

        elif command == '&bot_cards':
            if context != 'game':
                print("Command not work in menu.")
                input("Press Enter...")
                return
            print("\nBot cards:")
            print(" ".join(str(c) for c in self.bot.hand.cards) or "Is nothing")
            input("Press Enter...")

        else:
            print("Unknown command.")
            input("Press Enter...")



if __name__ == "__main__":
    Game().main_menu()