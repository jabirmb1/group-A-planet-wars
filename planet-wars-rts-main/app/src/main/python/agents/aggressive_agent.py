import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent)) # run code from python not agent

from agents.planet_wars_agent import PlanetWarsPlayer
from core.game_state import GameState, Action, Player, GameParams
from core.game_state_factory import GameStateFactory

# Attack enemy planets early 
# version 1

class AggresiveAgent(PlanetWarsPlayer):

    SAFETY_MARGIN = 1.2

    def get_action(self, game_state: GameState) -> Action:

        my_planets = [
            p for p in game_state.planets
            if p.owner == self.player and p.transporter is None and p.n_ships > 5
        ]
        if not my_planets:
            print("No available force mine")
            return Action.do_nothing()

        enemy_planets = [
            p for p in game_state.planets
            if p.owner not in (self.player, Player.Neutral)
        ]
        if not enemy_planets:
            print("No available enemy force")
            return Action.do_nothing()

        source = max(my_planets, key=lambda p: p.n_ships)

        best_target = None
        lowest_ships = float("inf")

        print("Chosen source my ships:", source.id, source.n_ships)


        for target in enemy_planets:
            print("Trying to find best enemy")
            
            if target.n_ships < lowest_ships and self.can_attack(target, source):
                lowest_ships = target.n_ships
                best_target = target

                print("Chosen target is best target:", best_target.id, best_target.n_ships)


        if best_target is None:
            print("No best target")
            return Action.do_nothing()


        return Action(
            player_id=self.player,
            source_planet_id=source.id,
            destination_planet_id=best_target.id,
            num_ships=int(source.n_ships * 0.75)
        )


    def get_agent_type(self) -> str:
        return "Aggressive Agent in Python"
    
    def can_attack(self, cur_target, source):
        # estimate attack outcome (borrowed idea from defensive agent)
        distance = source.position.distance(cur_target.position)
        eta = distance / self.params.transporter_speed
        estimated_defense = cur_target.n_ships + cur_target.growth_rate * eta

        required_ships = estimated_defense * self.SAFETY_MARGIN

        if source.n_ships <= required_ships:
            print("Not smart attack")
            return False
        
        return True





# Example usage
if __name__ == "__main__":
    agent = AggresiveAgent()
    agent.prepare_to_play_as(Player.Player1, GameParams())
    game_state = GameStateFactory(GameParams()).create_game()
    action = agent.get_action(game_state)
    print(action)