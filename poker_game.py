import random
from collections import Counter
from enum import Enum

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Rank(Enum):
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    ACE = (14, "A")
    
    def __init__(self, numeric_value, display):
        self._numeric_value = numeric_value
        self.display = display
    
    @property
    def numeric_value(self):
        return self._numeric_value

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank.display}{self.suit.value}"
    
    def __repr__(self):
        return str(self)

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal_card(self):
        return self.cards.pop()

# ...existing code...

class HandRank(Enum):
    HIGH_CARD = (1, "High Card")
    PAIR = (2, "Pair")
    TWO_PAIR = (3, "Two Pair")
    THREE_OF_A_KIND = (4, "Three of a Kind")
    STRAIGHT = (5, "Straight")
    FLUSH = (6, "Flush")
    FULL_HOUSE = (7, "Full House")
    FOUR_OF_A_KIND = (8, "Four of a Kind")
    STRAIGHT_FLUSH = (9, "Straight Flush")
    ROYAL_FLUSH = (10, "Royal Flush")

    def __init__(self, numeric_value, display):
        self._numeric_value = numeric_value
        self.display = display
    
    @property
    def numeric_value(self):
        return self._numeric_value

# ...existing code...

class PokerHand:
    def __init__(self, cards):
        self.cards = sorted(cards, key=lambda x: x.rank.numeric_value, reverse=True)
        self.rank, self.high_cards = self._evaluate_hand()
    
    def _evaluate_hand(self):
        ranks = [card.rank.numeric_value for card in self.cards]
        suits = [card.suit for card in self.cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = self._is_straight(ranks)
        
        # Royal Flush
        if is_flush and is_straight and min(ranks) == 10:
            return HandRank.ROYAL_FLUSH, []
        
        # Straight Flush
        if is_flush and is_straight:
            return HandRank.STRAIGHT_FLUSH, [max(ranks)]
        
        # Four of a Kind
        if 4 in rank_counts.values():
            quad = [rank for rank, count in rank_counts.items() if count == 4][0]
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.FOUR_OF_A_KIND, [quad, kicker]
        
        # Full House
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            trips = [rank for rank, count in rank_counts.items() if count == 3][0]
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            return HandRank.FULL_HOUSE, [trips, pair]
        
        # Flush
        if is_flush:
            return HandRank.FLUSH, sorted(ranks, reverse=True)
        
        # Straight
        if is_straight:
            return HandRank.STRAIGHT, [max(ranks)]
        
        # Three of a Kind
        if 3 in rank_counts.values():
            trips = [rank for rank, count in rank_counts.items() if count == 3][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.THREE_OF_A_KIND, [trips] + kickers
        
        # Two Pair
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            pairs = sorted(pairs, reverse=True)
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]
        
        # Pair
        if 2 in rank_counts.values():
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.PAIR, [pair] + kickers
        
        # High Card
        return HandRank.HIGH_CARD, sorted(ranks, reverse=True)
    
    def _is_straight(self, ranks):
        sorted_ranks = sorted(set(ranks))
        if len(sorted_ranks) < 5:
            return False
        
        # Check for regular straight
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i+4] - sorted_ranks[i] == 4:
                return True
        
        # Check for A-2-3-4-5 straight (wheel)
        if sorted_ranks == [2, 3, 4, 5, 14]:
            return True
        
        return False

class Player:
    def __init__(self, name, chips=1000, is_bot=False):
        self.name = name
        self.hand = []
        self.chips = chips
        self.current_bet = 0
        self.folded = False
        self.is_bot = is_bot
    
    def add_card(self, card):
        self.hand.append(card)
    
    def reset_hand(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
    
    def bet(self, amount):
        bet_amount = min(amount, self.chips)
        self.chips -= bet_amount
        self.current_bet += bet_amount
        return bet_amount

class BotPlayer(Player):
    def __init__(self, name, chips=1000):
        super().__init__(name, chips, is_bot=True)
        self.aggression = random.uniform(0.3, 0.8)  # How aggressive the bot is
        self.bluff_chance = random.uniform(0.1, 0.3)  # Chance to bluff
    
    def make_decision(self, current_bet_to_call, pot_size, community_cards, game_phase):
        """Simple bot AI for making decisions"""
        # Calculate hand strength (simplified)
        hand_strength = self._evaluate_hand_strength(community_cards)
        
        # Calculate pot odds
        if current_bet_to_call > 0:
            pot_odds = current_bet_to_call / (pot_size + current_bet_to_call)
        else:
            pot_odds = 0
        
        # Random factor for unpredictability
        random_factor = random.uniform(0.8, 1.2)
        adjusted_strength = hand_strength * random_factor
        
        # Decision logic
        if adjusted_strength < 0.2 and current_bet_to_call > self.chips * 0.1:
            return "fold"
        elif adjusted_strength > 0.7 or (random.random() < self.bluff_chance):
            if current_bet_to_call == 0:
                return "raise", min(int(pot_size * 0.5 * self.aggression), self.chips)
            elif adjusted_strength > 0.8:
                return "raise", min(int(current_bet_to_call * 2), self.chips)
            else:
                return "call"
        elif adjusted_strength > 0.4 or pot_odds < 0.3:
            return "call"
        else:
            return "fold"
    
    def _evaluate_hand_strength(self, community_cards):
        """Simple hand strength evaluation"""
        if not community_cards:
            # Preflop evaluation
            ranks = [card.rank.numeric_value for card in self.hand]
            if ranks[0] == ranks[1]:  # Pocket pair
                return 0.6 + (ranks[0] / 14) * 0.3
            elif abs(ranks[0] - ranks[1]) <= 3:  # Close ranks
                return 0.4 + (max(ranks) / 14) * 0.2
            else:
                return 0.2 + (max(ranks) / 14) * 0.2
        else:
            # Post-flop evaluation (simplified)
            all_cards = self.hand + community_cards
            from itertools import combinations
            
            # Check for pairs, straights, flushes, etc.
            ranks = [card.rank.numeric_value for card in all_cards]
            suits = [card.suit for card in all_cards]
            
            rank_counts = Counter(ranks)
            suit_counts = Counter(suits)
            
            if max(rank_counts.values()) >= 4:
                return 0.95  # Four of a kind or better
            elif max(rank_counts.values()) == 3:
                return 0.8   # Three of a kind
            elif len([c for c in rank_counts.values() if c >= 2]) >= 2:
                return 0.7   # Two pair or full house
            elif max(rank_counts.values()) == 2:
                return 0.5   # One pair
            elif max(suit_counts.values()) >= 5:
                return 0.85  # Flush
            else:
                return 0.3   # High card

class PokerGame:
    def __init__(self, human_players, total_players=6):
        self.deck = Deck()
        self.players = []
        
        # Add human players
        for name in human_players:
            self.players.append(Player(name))
        
        # Add bot players to reach total_players
        bot_names = ["Bot_Alpha", "Bot_Beta", "Bot_Gamma", "Bot_Delta", "Bot_Echo", 
                    "Bot_Foxtrot", "Bot_Golf", "Bot_Hotel"]
        bots_needed = total_players - len(human_players)
        
        for i in range(bots_needed):
            bot_name = bot_names[i % len(bot_names)]
            if i >= len(bot_names):
                bot_name += f"_{i // len(bot_names)}"
            self.players.append(BotPlayer(bot_name))
        
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.game_phase = "preflop"
        
        print(f"\nGame setup complete!")
        print(f"Human players: {[p.name for p in self.players if not p.is_bot]}")
        print(f"Bot players: {[p.name for p in self.players if p.is_bot]}")
        print(f"Total players: {len(self.players)}")
    
    def start_new_hand(self):
        print("\n" + "="*50)
        print("NEW HAND")
        print("="*50)
        
        # Reset everything
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.game_phase = "preflop"
        
        for player in self.players:
            player.reset_hand()
        
        # Deal hole cards
        for _ in range(2):
            for player in self.players:
                if not player.folded:
                    player.add_card(self.deck.deal_card())
        
        # Show player hands
        for player in self.players:
            print(f"{player.name}: {player.hand} (Chips: {player.chips})")
        
        self.betting_round()
    
    def betting_round(self):
        print(f"\n--- Betting Round ({self.game_phase}) ---")
        active_players = [p for p in self.players if not p.folded and p.chips > 0]
        
        if len(active_players) <= 1:
            return
        
        for player in active_players:
            if player.folded:
                continue
            
            call_amount = self.current_bet - player.current_bet
            
            if player.is_bot:
                # Bot decision making
                decision = player.make_decision(call_amount, self.pot, self.community_cards, self.game_phase)
                
                if decision == "fold":
                    player.folded = True
                    print(f"{player.name} (Bot) folds")
                elif decision == "call":
                    actual_bet = player.bet(call_amount)
                    self.pot += actual_bet
                    if call_amount == 0:
                        print(f"{player.name} (Bot) checks")
                    else:
                        print(f"{player.name} (Bot) calls {actual_bet}")
                elif isinstance(decision, tuple) and decision[0] == "raise":
                    raise_amount = decision[1]
                    total_bet = call_amount + raise_amount
                    actual_bet = player.bet(total_bet)
                    self.pot += actual_bet
                    self.current_bet = player.current_bet
                    print(f"{player.name} (Bot) raises by {raise_amount} (total bet: {actual_bet})")
            else:
                # Human player input
                print(f"\n{player.name}'s turn:")
                print(f"Your hand: {player.hand}")
                if self.community_cards:
                    print(f"Community cards: {self.community_cards}")
                print(f"Your chips: {player.chips}")
                print(f"Current bet to call: {call_amount}")
                print(f"Pot: {self.pot}")
                
                while True:
                    if call_amount == 0:
                        action = input("Action: (ch)eck, (r)aise, (f)old, (a)ll-in: ").lower()
                    else:
                        action = input("Action: (f)old, (c)all, (r)aise, (a)ll-in: ").lower()
                    
                    if action in ['f', 'fold']:
                        player.folded = True
                        print(f"{player.name} folds")
                        break
                    elif action in ['c', 'call'] and call_amount > 0:
                        actual_bet = player.bet(call_amount)
                        self.pot += actual_bet
                        print(f"{player.name} calls {actual_bet}")
                        break
                    elif action in ['ch', 'check'] and call_amount == 0:
                        print(f"{player.name} checks")
                        break
                    elif action in ['r', 'raise']:
                        try:
                            max_raise = player.chips - call_amount
                            raise_amount = int(input(f"Raise amount (max {max_raise}): "))
                            if raise_amount > max_raise:
                                print("Not enough chips for that raise!")
                                continue
                            total_bet = call_amount + raise_amount
                            actual_bet = player.bet(total_bet)
                            self.pot += actual_bet
                            self.current_bet = player.current_bet
                            print(f"{player.name} raises by {raise_amount}")
                            break
                        except ValueError:
                            print("Invalid amount, please try again")
                    elif action in ['a', 'all-in', 'allin']:
                        actual_bet = player.bet(player.chips)
                        self.pot += actual_bet
                        self.current_bet = max(self.current_bet, player.current_bet)
                        print(f"{player.name} goes all-in for {actual_bet}")
                        break
                    else:
                        print("Invalid action, please try again")
    
    def deal_flop(self):
        self.game_phase = "flop"
        self.deck.deal_card()  # Burn card
        for _ in range(3):
            self.community_cards.append(self.deck.deal_card())
        print(f"\nFLOP: {self.community_cards}")
        self.betting_round()
    
    def deal_turn(self):
        self.game_phase = "turn"
        self.deck.deal_card()  # Burn card
        self.community_cards.append(self.deck.deal_card())
        print(f"\nTURN: {self.community_cards}")
        self.betting_round()
    
    def deal_river(self):
        self.game_phase = "river"
        self.deck.deal_card()  # Burn card
        self.community_cards.append(self.deck.deal_card())
        print(f"\nRIVER: {self.community_cards}")
        self.betting_round()
    
    def showdown(self):
        print("\n" + "="*30)
        print("SHOWDOWN")
        print("="*30)
        
        active_players = [p for p in self.players if not p.folded]
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.pot
            print(f"{winner.name} wins {self.pot} chips (everyone else folded)")
            return
        
        # Evaluate hands
        player_hands = []
        for player in active_players:
            all_cards = player.hand + self.community_cards
            best_hand = self.get_best_five_card_hand(all_cards)
            player_hands.append((player, best_hand))
            print(f"{player.name}: {player.hand} -> Best hand: {[str(c) for c in best_hand.cards]} ({best_hand.rank.name})")
        
        # Find winner
        winner = max(player_hands, key=lambda x: (x[1].rank.numeric_value, x[1].high_cards))
        winner[0].chips += self.pot
        print(f"\n{winner[0].name} wins {self.pot} chips!")
    
    def get_best_five_card_hand(self, cards):
        from itertools import combinations
        best_hand = None
        
        for combo in combinations(cards, 5):
            hand = PokerHand(list(combo))
            if best_hand is None or (hand.rank.numeric_value > best_hand.rank.numeric_value or 
                                   (hand.rank.numeric_value == best_hand.rank.numeric_value and hand.high_cards > best_hand.high_cards)):
                best_hand = hand
        
        return best_hand
    
    def play_hand(self):
        self.start_new_hand()
        
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) > 1:
            self.deal_flop()
        
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) > 1:
            self.deal_turn()
        
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) > 1:
            self.deal_river()
        
        self.showdown()

def main():
    print("Welcome to Python Poker!")
    print("This is a simplified Texas Hold'em game.")
    
    # Get player names
    num_players = int(input("Number of players (2-6): "))
    player_names = []
    for i in range(num_players):
        name = input(f"Enter name for player {i+1}: ")
        player_names.append(name)
    
    game = PokerGame(player_names)
    
    while True:
        # Check if anyone is out of chips
        active_players = [p for p in game.players if p.chips > 0]
        if len(active_players) < 2:
            print("\nGame Over!")
            if active_players:
                print(f"{active_players[0].name} wins the game!")
            break
        
        game.play_hand()
        
        # Show chip counts
        print("\nChip counts:")
        for player in game.players:
            if player.chips > 0:
                print(f"{player.name}: {player.chips}")
        
        play_again = input("\nPlay another hand? (y/n): ").lower()
        if play_again != 'y':
            break
    
    print("Thanks for playing!")

if __name__ == "__main__":
    main()