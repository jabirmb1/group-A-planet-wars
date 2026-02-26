import sys
from pathlib import Path

# Add the parent directory to Python path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.planet_wars_agent import PlanetWarsPlayer
from core.game_state import GameState, Action, Player, GameParams
from core.game_state_factory import GameStateFactory

# Attack enemy planets early 
# version 1

class AggresiveAgent(PlanetWarsPlayer):
    # No distance limit — attack anything reachable

    # action that the agnet will take
    def get_action(self, game_state: GameState) -> Action:

        # Filter own planets that are not busy and have enough ships
        my_planets = [p for p in game_state.planets
                      if p.owner == self.player and p.transporter is None and p.n_ships > 5]
        if not my_planets:
            print("no planet my")
            return Action.do_nothing()
        

        # all enymy planet
        enemy_planets = [p for p in game_state.planets if p.owner not in (self.player, Player.Neutral)]
        if not enemy_planets:
            print("no enemy planet available")
            return Action.do_nothing()
        

        # Pick your planet with most ships
        source = max(my_planets, key=lambda p: p.n_ships)

        best_target = None # chosen ship
        lowest_ships = float("inf")

        # pick weakest enemy planet
        for cur_choice in enemy_planets:
            # choose the weakest planet
            if cur_choice.n_ships < lowest_ships:
                lowest_ships = cur_choice.n_ships
                best_target = cur_choice

        if best_target is None:
            return Action.do_nothing()

        print(f"Source planet {source.id} has {source.n_ships} ships")
        print(f"Target planet {best_target.id} has {best_target.n_ships} ships")

        # Simple check: only attack if we have more ships
        if source.n_ships <= best_target.n_ships:
            print(f"❌ Not strong enough ({source.n_ships} <= {best_target.n_ships})")
            return Action.do_nothing()

        print(f"✅ Attacking {best_target.id} with {source.n_ships * 3 // 4} ships")
        return Action(
            player_id=self.player,
            source_planet_id=source.id,
            destination_planet_id=best_target.id,
            num_ships=source.n_ships * 3 // 4
        )


    def get_agent_type(self) -> str:
        return "Aggressive Agent in Python"



# Example usage
if __name__ == "__main__":
    agent = AggresiveAgent()
    agent.prepare_to_play_as(Player.Player1, GameParams())
    game_state = GameStateFactory(GameParams()).create_game()
    action = agent.get_action(game_state)
    print(action)