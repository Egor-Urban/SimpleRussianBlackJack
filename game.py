# Simple Russian Blackjack in terminal
# Version: 3.4.18 r
# Developer: Urban Egor

import random
import os
import time



# --- CONSTs ---
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


    def __repr__(self):
        return str(self)



class Deck:
    def __init__(self):
        self.reset()


    def reset(self):
        self.cards = [Card(rank, suit) for rank in RANKS for suit in SUITS]
        random.shuffle(self.cards)
        self.used = []


    def draw(self):
        if not self.cards:
            raise RuntimeError("Deck is empty now.")
        card = self.cards.pop()
        self.used.append(card)
        return card


    def remove_except(self, keep_cards):
        keep_set = {(c.rank, c.suit) for c in keep_cards}
        self.cards = [c for c in self.cards if (c.rank, c.suit) in keep_set]
        self.used = [c for c in self.used if (c.rank, c.suit) in keep_set]


    def remaining(self):
        return len(self.cards)


    def __str__(self):
        return " ".join(str(card) for card in self.cards)



# ----
class Hand:
    def __init__(self):
        self.crds = []


    def add(self, card):
        self.crds.append(card)


    def get_score(self):
        return sum(c.value for c in self.crds)


    def is_bust(self):
        return self.get_score() > 21


    def show(self, hidden=False):
        if hidden and len(self.crds) > 1:
            return "[??] " + " ".join(str(c) for c in self.crds[1:])
        return " ".join(str(c) for c in self.crds)



class Player:
    def __init__(self, name, coins=100):
        self.name = name
        self.coins = coins
        self.hand = Hand()
        self.wins = 0
        self.losses = 0


    def reset_hand(self):
        self.hand = Hand()


    def add_card(self, card):
        self.hand.add(card)


    def score(self):
        return self.hand.get_score()


    def is_bust(self):
        return self.hand.is_bust()


    def can_bet(self, amount):
        return self.coins >= amount



class HumanPlayer(Player):
    def take_turn(self, deck, game=None):
        while True:
            print(f"\nYour cards: {self.hand.show()} | Score: {self.score()}")
            if self.is_bust():
                print("Too much!")
                break
            choice = input("Take card? [y/n or &command]: ").strip().lower()
            if choice.startswith("&") and game:
                game.debug_command(choice)
                continue
            if choice in ("д", "y"):
                try:
                    self.add_card(deck.draw())
                except RuntimeError:
                    print("❌ Deck is gone.")
                    break
            elif choice in ("н", "n"):
                break



class BotPlayer(Player):
    def __init__(self, name, dificalty='normal', coins=100):
        super().__init__(name, coins)
        self.dificalty = dificalty


    def take_turn(self, deck, game=None):
        while True:
            score = self.score()
            safe_cards = [c for c in deck.cards if self._would_not_bust(score, c)]
            threshold = DIFFICULTY_THRESHOLDS[self.dificalty]
            prob = len(safe_cards) / len(deck.cards) if deck.cards else 0
            if score < 17 and prob > threshold:
                try:
                    self.add_card(deck.draw())
                    time.sleep(1)
                except RuntimeError:
                    print("❌ Deck is gone.")
                    break
            else:
                break


    def _would_not_bust(self, score, card):
        value = 1 if card.rank == 'A' and score + 1 <= 21 else card.value
        return score + value <= 21


    def choose_bet(self, opp_coins):
        min_bet, max_bet = BET_RANGES[self.dificalty]
        bet = random.randint(min_bet, max_bet)
        return min(bet, self.coins, opp_coins)



class Game:
    def __init__(self):
        self.deck = Deck()
        self.dificalty = 'normal'
        self.human = HumanPlayer("Player")
        self.bot = BotPlayer("Bot", dificalty=self.dificalty)
        self.bet = 0


    def main_menu(self):
        while True:
            self.clear_screen()
            print("===== Russian BlackJack =====")
            print(f"Coins: Player — {self.human.coins}, Bot — {self.bot.coins}")
            print(f"Wins: {self.human.wins} | Loses: {self.human.losses}")
            print("1 - Start game")
            print("2 - Bot setting (now: {})".format(self.bot.dificalty))
            print("3 - Rules")
            print("4 - Exit")

            choice = input("Choice: ").strip()

            if choice.startswith('&'):
                self.debug_command(choice, context='menu')
                continue

            if choice == '1':
                self.play()
            elif choice == '2':
                self.configure_bot()
            elif choice == '3':
                self.rules()
            elif choice == '4':
                break

    def rules(self):
        self.clear_screen()
        print('King = 4, Queen = 3, Jack = 2, Ace = 11, and Ace + Ace = 21. ')
        print("DEBUG commands:")
        print("&rm_cards - clear deck")
        print("&get_money_{count} - gives the player money")
        print("&bot_cards - show bot cards")
        print("&ingame_cards - shows the remaining cards in the deck")
        print('commands working in game and some in main menu')
        x = input("Press Enter...")

    def configure_bot(self):
        self.clear_screen()
        print("Choose bot level:")
        print("1 - Easy")
        print("2 - Normal")
        print("3 - Hard")
        mapping = {'1': 'easy', '2': 'normal', '3': 'hard'}
        choice = input("Choice: ").strip()
        self.dificalty = mapping.get(choice, self.dificalty)
        self.bot = BotPlayer("Bot", dificalty=self.dificalty, coins=self.bot.coins)


    def play(self):
        if self.human.coins == 0:
            print("You got no coins. Game over.")
            input("Press Enter...")
            return
        if self.bot.coins == 0:
            print("Bot is out of coins. You win!")
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

        self.clear_screen()
        first = random.choice([self.human, self.bot])
        second = self.bot if first == self.human else self.human

        print("===== New Round =====")
        print(f"{self.human.name}: {self.human.coins} coins")
        print(f"{self.bot.name}: {self.bot.coins} coins")
        print(f"\nFirst move: {first.name}")

        self.bet = self.make_bet(first, second)
        if self.bet == 0:
            print("Bet not possible. Skip round.")
            input("Press Enter...")
            return

        try:
            first.take_turn(self.deck, self if isinstance(first, HumanPlayer) else None)
            self.clear_screen()
            second.take_turn(self.deck, self if isinstance(second, HumanPlayer) else None)
        except RuntimeError:
            self.handle_deck_exhaustion()
            return

        self.resolve()


    def handle_deck_exhaustion(self):
        print("\n❌ Deck is gone!")
        h_crds = self.human.hand.crds
        b_crds = self.bot.hand.crds

        if not h_crds or not b_crds:
            print("No winner. Someone got no cards.")
        else:
            h_score = self.human.score()
            b_score = self.bot.score()
            print(f"Your cards: {self.human.hand.show()} | Score: {h_score}")
            print(f"Bot cards: {self.bot.hand.show()} | Score: {b_score}")
            resalt = self.determine_winner(h_score, b_score)
            print(f"Result: {resalt}")
            self.update_score(resalt)

        input("\nPress Enter to continue...")


    def resolve(self):
        h_score = self.human.score()
        b_score = self.bot.score()
        print("\n--- Results ---")
        print(f"Your cards: {self.human.hand.show()} | Score: {h_score}")
        print(f"Bot cards: {self.bot.hand.show()} | Score: {b_score}")
        resalt = self.determine_winner(h_score, b_score)
        print(f"Result: {resalt}")
        self.update_score(resalt)
        input("\nPress Enter to continue...")


    def update_score(self, resalt):
        if "you win" in resalt:
            self.human.coins += self.bet
            self.bot.coins -= self.bet
            self.human.wins += 1
            self.bot.losses += 1
        elif "you lose" in resalt:
            self.human.coins -= self.bet
            self.bot.coins += self.bet
            self.human.losses += 1
            self.bot.wins += 1


    def determine_winner(self, h, b):
        if h > 21 and b > 21:
            return "Both bust. Draw."
        if h > 21:
            return "You lose. Bust."
        if b > 21:
            return "You win! Bot bust."
        if h > b:
            return "You win!"
        if b > h:
            return "You lose."
        return "Draw."


    def make_bet(self, initiator, opponent):
        if isinstance(initiator, BotPlayer):
            bet = initiator.choose_bet(opponent.coins)
            print(f"Bot bet {bet} coins.")
            input("Press Enter to go...")
            return bet
        while True:
            print(f"\nHow many coins to bet? (you: {initiator.coins}, enemy: {opponent.coins})")
            try:
                bet = int(input("Bet: ").strip())
                if 1 <= bet <= min(initiator.coins, opponent.coins):
                    return bet
            except:
                pass
            print("Bad bet.")


    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def debug_command(self, command, context='game'):
        allowed_in_menu = {'&ingame_cards', '&rm_cards'}
        if command.startswith('&get_money_'):
            try:
                amount = int(command.split('_')[-1])
                self.human.coins += amount
                print(f"Got {amount} coins.")
                input("Press Enter...")
            except:
                print("Wrong format.")
                input("Press Enter...")
            return

        if context == 'menu' and command not in allowed_in_menu:
            print("Command no can in menu.")
            input("Press Enter...")
            return

        if command == '&ingame_cards':
            print("\nLeft cards in deck:")
            print(str(self.deck) or "Deck is empty")
            input("Press Enter...")

        elif command == '&rm_cards':
            keep = self.human.hand.crds + self.bot.hand.crds
            self.deck.remove_except(keep)
            print("Deck cleaned. Only game cards here.")
            input("Press Enter...")

        elif command == '&bot_cards':
            print("\nBot cards:")
            print(" ".join(str(c) for c in self.bot.hand.crds) or "None")
            input("Press Enter...")

        else:
            print("Unknown command.")
            input("Press Enter...")



if __name__ == "__main__":
    Game().main_menu()