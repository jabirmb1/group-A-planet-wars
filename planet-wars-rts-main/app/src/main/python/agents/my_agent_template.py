"""
Template for creating a new Planet Wars Agent.

Copy this file and rename it to your_agent_name.py, then customize the logic
in get_action() to implement your strategy.
"""

from agents.planet_wars_agent import PlanetWarsPlayer
from core.game_state import GameState, Action, Player, GameParams


class MyCustomAgent(PlanetWarsPlayer):
    """
    A simple template agent for Planet Wars RTS.
    
    Inherit from PlanetWarsPlayer to get access to:
    - self.player: your player ID (Player.Player1 or Player.Player2)
    - self.params: current game parameters (GameParams)
    """

    def __init__(self):
        """Initialize your agent. Called once at creation."""
        super().__init__()
        # Add any custom initialization here
        self.move_count = 0

    def get_action(self, game_state: GameState) -> Action:
        """
        Decide what action to take each game turn.
        
        Args:
            game_state: The current state of the game (fully observable).
        
        Returns:
            An Action object representing your move, or Action.do_nothing().
        
        Key GameState properties:
            - game_state.planets: List of all planets
            - game_state.current_player: Whose turn it is
            - game_state.tick: Current game tick/turn number
            
        Key Planet properties:
            - planet.owner: Who owns it (Player.Player1, Player.Player2, or Player.Neutral)
            - planet.n_ships: Number of ships on the planet
            - planet.growth_rate: Ships produced per turn
            - planet.position: (x, y) coordinates
            - planet.id: Unique identifier
        """
        self.move_count += 1
        
        # Example strategy: Find any friendly planet and attack a neutral target
        
        # 1. Find planets you own that can send ships (not busy, have ships)
        my_planets = [
            p for p in game_state.planets 
            if p.owner == self.player and p.transporter is None and p.n_ships > 5
        ]
        
        if not my_planets:
            # No valid source planets
            return Action.do_nothing()
        
        # 2. Find targets (planets not owned by you)
        targets = [p for p in game_state.planets if p.owner != self.player]
        
        if not targets:
            # No targets available (you own everything!)
            return Action.do_nothing()
        
        # 3. Pick source: the planet with the most ships
        source = max(my_planets, key=lambda p: p.n_ships)
        
        # 4. Pick target: closest one (simple heuristic)
        target = min(targets, key=lambda t: source.position.distance(t.position))
        
        # 5. Send half the ships from source to target
        num_ships = int(source.n_ships / 2)
        
        return Action(
            player_id=self.player,
            source_planet_id=source.id,
            destination_planet_id=target.id,
            num_ships=num_ships
        )

    def get_agent_type(self) -> str:
        """Return a human-readable name for your agent."""
        return "My Custom Agent"

    def prepare_to_play_as(self, player: Player, params: GameParams, opponent=None) -> str:
        """
        Called before the game starts. Set up your agent for a specific player/game.
        
        Args:
            player: Your player ID (Player.Player1 or Player.Player2)
            params: Game parameters (number of planets, speeds, etc.)
            opponent: Opponent name (optional)
        """
        super().prepare_to_play_as(player, params, opponent)
        self.move_count = 0
        print(f"Preparing {self.get_agent_type()} to play as {player} with {params.num_planets} planets")
        return self.get_agent_type()

    def process_game_over(self, final_state: GameState) -> None:
        """
        Called when the game ends. Use this for training/learning logic.
        
        Args:
            final_state: The final game state (fully observable).
        """
        winner = final_state.get_winner()
        print(f"Game over! Winner: {winner}. My agent ({self.player}) made {self.move_count} moves.")


# ============================================
# Example usage: test your agent
# ============================================

if __name__ == "__main__":
    from core.game_state_factory import GameStateFactory
    from core.game_runner import GameRunner
    
    # Create your agent
    agent = MyCustomAgent()
    
    # Prepare it to play
    game_params = GameParams(num_planets=10)
    agent.prepare_to_play_as(Player.Player1, game_params)
    
    # Create an initial game state and get an action
    game_state = GameStateFactory(game_params).create_game()
    action = agent.get_action(game_state)
    
    print(f"Agent type: {agent.get_agent_type()}")
    print(f"First action: {action}")
