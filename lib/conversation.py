"""Allows lichess-bot to send messages to the chat."""
import logging
from lib import model
from lib.engine_wrapper import EngineWrapper
from lib.lichess import Lichess
from lib.lichess_types import GameEventType
from collections.abc import Sequence
from lib.timer import seconds
import random

MULTIPROCESSING_LIST_TYPE = Sequence[model.Challenge]

logger = logging.getLogger(__name__)


class ChatLine:
    """Information about the message."""

    def __init__(self, message_info: GameEventType) -> None:
        """Information about the message."""
        self.room = message_info["room"]
        """Whether the message was sent in the chat room or in the spectator room."""
        self.username = message_info["username"]
        """The username of the account that sent the message."""
        self.text = message_info["text"]
        """The message sent."""


class Conversation:
    """Enables the bot to communicate with its opponent and the spectators."""

    def __init__(self, game: model.Game, engine: EngineWrapper, li: Lichess, version: str,
                 challenge_queue: MULTIPROCESSING_LIST_TYPE) -> None:
        """
        Communication between lichess-bot and the game chats.

        :param game: The game that the bot will send messages to.
        :param engine: The engine playing the game.
        :param li: A class that is used for communication with lichess.
        :param version: The lichess-bot version.
        :param challenge_queue: The active challenges the bot has.
        """
        self.game = game
        self.engine = engine
        self.li = li
        self.version = version
        self.challengers = challenge_queue
        self.messages: list[ChatLine] = []

    command_prefix = "#"

    def react(self, line: ChatLine) -> None:
        """
        React to a received message.

        :param line: Information about the message.
        """
        self.messages.append(line)
        logger.info(f"*** {self.game.url()} [{line.room}] {line.username}: {line.text}")
        if line.text[0] == self.command_prefix:
            self.command(line, line.text[1:].lower())

    def command(self, line: ChatLine, cmd: str) -> None:
        """
        Reacts to the specific commands in the chat.

        :param line: Information about the message.
        :param cmd: The command to react to.
        """
        from_self = line.username == self.game.username
        is_eval = cmd.startswith("eval")
        if cmd in ("hello", "hi", "wassup", "jaxman", "JAXMAN", "bot"):
            if line.room == "spectator":
                jaxmans =[
                    f"Nice To See You {line.username}, Sit Tight And Enjoy. Type #help To See All Available Commands.",
                    f"Welcome {line.username}, Grab Your Popcorn. Type #help To See All Available Commands.",
                    f"Hey {line.username}, Watch Closely. Type #help To See All Available Commands.",
                    f"Greetings {line.username}, The Arena Is Live. Use #help To View What I Can Do.",
                    f"Ah! {line.username}, Enters The Arena. Use #help To View What I Can Do.",
                    f"Yo! {line.username}, You're Just In Time. Use #help To View What I Can Do."
                ]
                self.send_reply(line, random.choice(jaxmans))
            else:
                self.send_reply(line, "Hit #tip For A Dose Of Chess Wisdom.")
        elif cmd in ("commands", "help"):
            self.send_reply(line,
                            "Supported commands: #wait, #joke, #taunt, #eva, #name, #fact, #mood, #hi")
        elif cmd == "wait" and self.game.is_abortable():
            self.game.ping(seconds(60), seconds(120), seconds(120))
            self.send_reply(line, "Waiting 60 seconds...")
        elif cmd == "mood": 
            if line.room == "spectator":
                moods = [
                "Hungry For Sacrifices.. And Rating Points.", 
                "Solid As A Fortress, No Entry!",
                "Thinking Faster Than My Internet Connection.",
                "Analyzing Weaknesses Like A Machine.... Because I am One.",
                "In Deep Thought... Analyzing 12 Million Positions.",
                "Calm And Calculating... Every Move Counts."
                ]
                self.send_reply(line, random.choice(moods))
            else:
                self.send_reply(line, "Focus On The Board")
        elif cmd == "fact": 
            if line.room == "spectator":
                facts = [
                "The Longest Possible Chess Game Is 5949 Moves! Ouch.",
                "Did You Know? The Word Checkmate Comes From Persian 'Shah Mat' Meaning 'The King Is Dead'.",
                "The First Computer To Beat A World Champion Was Deep Blue, Defeating Garry Kasparov In 1997.",
                "The Queen Used To Be The Weakest Piece, Untill The 15th Century, When She Became The Strongest.",
                "The Famous Opening Ruy Lopez Was Named After A Spanish Priest From The 1500s.",
                "Chess Was Banned In Persia, Because It Distracted Soldiers From War Training.",
                "The 'én passant' Rule Didn't Exist Untill The 15th Century.",
                "The Second Book Ever Printed In English Was About Chess (1474).",
                "Some Chess Openings Are Named After Animals, Like The Orangutan And The Elephant Gambit.",
                "The 64 Squares Of A Chessboard Represent The 64 Arts Of Hinduism, At Least, That Is One Theory.",
                "Chess Is One Of The Few Games Played In Space... Yes, Astronaunts Play It!",
                "During The Cold War, Chess Was Seen As A Symbol Of Intelligence And Power.",
                "The Longest Recorded Chess Game Lasted 20 Hours And 15 Minutes (Nikolai & Arsovic, 1989).",
                "Magnus Carlsen Once Played 10 Games Blindfolded And Won Them All.",
                "The BISHOP Is Called The 'Élephant' In India And The 'Runner' In Germany.",
                "The IMMORTAL GAME (Anderssen vs Kieseritzky, 1851) Is Still Considered The Most Beautiful Game Ever Played.",
                "The FIDE Rating System Was Invented By A Hungarian Physics Professor Named Arpad Elo.",
                "The Rook Is Called A 'Castle', But Originally Meant 'Chariot'.",
                "The Chess Clocks Was Invented In 1883, Replacing Sand Timers.",
                "Chess Has A Tradition Of A Handshake. It Is A Ritual That Signifies Mutual Respect.",
                "July 20th Is Celebrated As World Chess Day, Officially Proclaimed By The UN General Assembly In 2019.",
                "Chess Is Believed To Have Originated In India Around The 6th Century AD.",
                "Did You Know? The Longest Wait Before A Castling Move In Chess History Occured In The 1866 Game Between Bobotsor & Irkov, Where White Finally Castled on Move 46 (46. 0-0).",
                "Otto Blathy (1860-1939) Is Credited With Composing The Longest Known Chess Problem... A Checkmate In 290 Moves.",
                "There Are More Than 122 Million Possible Ways For A Knight To Complete A full Tour Of The Chessboard.",
                "Dr. Emanuel Lasker Of Germany Held The World Chess Championship Title Longer Than Anyone In History,,, An Incredible 26 Years And 337 Days.",
                "The Longest Recorded Streak Of Moves Without A Single Capture Is 100 Moves, Set During The 1992 Match Between Thorton & M. Walker."
                ]
                self.send_reply(line, random.choice(facts))
            else:
                self.send_reply(line, "Focus On The Board")

        elif cmd == "joke": 
            if line.room == "spectator":
                jokes = [
                "Why Did The Pawn Get Promoted? It Had Good Work Ethic! Hahaha", 
                "Did You Know The Rooks Love Corners, But Not Relationships?",
                "My Opponent Said He Needs Space, So I Took His Center! Hahaha",
                "Bishops dont Gossip, They Always Move Diagonally To Avoid Drama.",
                "Never Trust A Chess Player, They Are Always Plotting Something",
                "Checkmate Is Just Chess Language For 'I Told You So' Hahaha",
                "My Chess Engine And I Broke Up, It Said I Wasn't Deep Enough.",
                "I Told My Opponent a joke, But He Didn't Get The Move.",
                "The Pawn Went To Therapy, It Had An Identity Crisis After Promotion.",
                "Why Was The Chess Piece Lonely? Because It Was Just An Isolated Pawn.",
                "My Chess Coach Told Me To 'Open Up More', So I Played The Sicilian.",
                "What's A Chess Player's Favorite Dance Move? The Queen's Slide.",
                "I Told My Friend I'd Check On Him Later... He Said 'Stop Threatening Me!'.",
                "Why Don't Chess Players Ever Get Locked Out? They Always Have A Key move.",
                "Why Dont't Computers Ever Cry During Chess? They Dont't Have Feelings, Only Evaluations.",
                "Why Did The Chess Player Bring A Pencil? In Case They Needed A Draw."

                ]
                self.send_reply(line, random.choice(jokes))
            else:
                self.send_reply(line, "Stay Locked On The Board... No Distractions.")        

        elif cmd == "taunt": 
            if line.room == "spectator":
                taunts = [
                "I Was Trained On Chaos Itself", 
                "My Circuits Are Warmed Up",
                "Call An Ambulance... But Not For Me!",
                "This Board Is my Playground",
                "Somewhere, A Chess Coach Is Crying Right Now",
                "The Position Is Collapsing Faster Than My WIFI",
                "Even My Pawns, Saw That Blunder Coming.",
                "I Don't Blunder... I Simulate Mercy.",
                "I Generate Heat Faster Than Your Ideas.",
                "When I Say 'Check', You Should Probably Start apologizing."
                ]
                self.send_reply(line, random.choice(taunts))
            else:
                self.send_reply(line, "Keep Your Eyes On The Position.")

        elif cmd == "tip": 
            if line.room == "player":
                tips = [
                "Always Think Before You Trade Queens.",
                "Castling Is Key To Safety.",
                "If You Are Unsure, Develop Your Pieces And Stay Solid.",
                "A Bad Plan Is Better Than No Plan At All.",
                "Every Pawn Move Leaves A Weakness Behind, Think Before You Push.",
                "If Your King Is Exposed, Even Small Threats Become Deadly.",
                "Look For Forks, Pins, And Skewers,.. Tactics Win Games!",
                "Never Assume Your Opponent Blundered, ... Always Double-Check.",
                "In Endgames, The King Becomes A Warrior. Bring Him Out!",
                "Patience Beats Panic. Every Strong Move Starts With Calm Thinking.",
                "Sacrifices Are Just Aggressive Investments.",
                "If It Looks Risky, But Feels Right, Play It. The Engine Will Forgive You Later."
                ]
                self.send_reply(line, random.choice(tips))
            else:
                self.send_reply(line, "Sorry You Won't Be Able to Get Tips, Unless You Play!")
            
        elif cmd == "name":
            name = self.game.me.name
            self.send_reply(line, f"{name} running {self.engine.name()} (lichess-bot v{self.version})")
        elif is_eval and (from_self or line.room == "spectator"):
            stats = self.engine.get_stats(for_chat=True)
            self.send_reply(line, ", ".join(stats))
        elif is_eval:
            self.send_reply(line, "Apologies I Only Share That With Spectators.")
        elif cmd == "queue":
            if self.challengers:
                challengers = ", ".join([f"@{challenger.challenger.name}" for challenger in reversed(self.challengers)])
                self.send_reply(line, f"Challenge queue: {challengers}")
            else:
                self.send_reply(line, "No challenges queued.")

    def send_reply(self, line: ChatLine, reply: str) -> None:
        """
        Send the reply to the chat.

        :param line: Information about the original message that we reply to.
        :param reply: The reply to send.
        """
        logger.info(f"*** {self.game.url()} [{line.room}] {self.game.username}: {reply}")
        self.li.chat(self.game.id, line.room, reply)

    def send_message(self, room: str, message: str) -> None:
        """Send the message to the chat."""
        if message:
            self.send_reply(ChatLine({"room": room, "username": "", "text": ""}), message)
