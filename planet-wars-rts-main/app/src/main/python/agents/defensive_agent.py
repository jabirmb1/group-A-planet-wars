import math
from typing import Optional

from agents.planet_wars_agent import PlanetWarsPlayer
from core.game_state import GameState, Action, Player, GameParams, Planet


class DefensiveTurtleAgent(PlanetWarsPlayer):
    """
    defensive agent that prioritizes survival over expansion.
    The priorities for the turtle agent are:
    - Defend threatened planets first
    - Maintain reserves on all planets
    - Attack weak and high growth rate targets when safe
    """

    def __init__(self):
        """Strategy parameters initialization."""
        super().__init__()
        self.SAFETY_MULTIPLIER = 1.5                  # Safety margin when deciding to attack
        self.REINFORCEMENT_RESERVE = 0.5              # Ratio to keep back when reinforcing threatened friendly planets
        self.ATTACK_RESERVE = 0.7                     # To keep back a percentage of ships while attacking
        self.MIN_ATTACK_SHIPS = 20                    # The minimum ships required for a planet to initiate an attack

    def get_action(self, game_state: GameState) -> Action:
        planet_by_id = {p.id: p for p in game_state.planets}                     # Dictionary for all planets by id
        my_planets = [p for p in game_state.planets if p.owner == self.player]   # Dictionary for my planet(s)

        """Defending: Checking for enemy transporters into friendly planets
        and sending reinforcement if needed"""
        for planet in game_state.planets:
            if planet.owner != self.player and planet.owner != Player.Neutral:
                fleet = planet.transporter

                if fleet is not None:
                    dest_id = fleet.destination_index
                    dest_planet = planet_by_id[dest_id]

                    if dest_planet.owner == self.player:
                        # Calculate if we need reinforcement
                        shortfall = self.calculate_shortfall(fleet, dest_planet)

                        if shortfall > 0:
                            # Send reinforcement
                            action = self.send_reinforcement(my_planets, dest_planet, dest_id, shortfall)
                            if action is not None:
                                return action

        """Attacking: Checking for weak enemy planets with high growth rate to attack friendly
        with a strong source"""
        attack_sources = [p for p in my_planets if p.transporter is None and p.n_ships > 20]

        if attack_sources:
            potential_targets = [p for p in game_state.planets if p.owner != self.player]

            if potential_targets:
                # Pick target and source
                target = min(potential_targets, key=lambda p: (p.n_ships, -p.growth_rate))
                source = max(attack_sources, key=lambda p: (p.n_ships, -p.position.distance(target.position)))

                # Try to attack
                action = self.attempt_attack(source, target)
                if action is not None:
                    return action

        return Action.do_nothing()

    def calculate_shortfall(self, fleet, dest_planet) -> float:
        """Calculate how many more ships we need to defend"""
        distance = fleet.s.distance(dest_planet.position)
        speed = fleet.v.mag()
        turns_until_arrival = distance / speed if speed > 0 else float("inf")

        enemy_ships = fleet.n_ships
        current_ships = dest_planet.n_ships
        production = dest_planet.growth_rate * turns_until_arrival
        my_ships_at_arrival = current_ships + production

        ships_required = enemy_ships * self.SAFETY_MULTIPLIER
        return ships_required - my_ships_at_arrival

    def send_reinforcement(self, my_planets, dest_planet, dest_id, shortfall) -> Optional[Action]:
        """Send reinforcements to threatened planet"""
        helpers = [p for p in my_planets if p.id != dest_id and p.transporter is None]

        if not helpers:
            return None

        source = max(helpers, key=lambda p: (p.n_ships, -p.position.distance(dest_planet.position)))
        spare = source.n_ships * (1 - self.DEFENSE_RESERVE)

        if spare >= shortfall:
            send = min(int(spare), math.ceil(shortfall))
            return Action(
                player_id=self.player,
                source_planet_id=source.id,
                destination_planet_id=dest_id,
                num_ships=send
            )

        return None

    def attempt_attack(self, source, target) -> Optional[Action]:
        """Try to attack a target if it is safe, and we can most likely win"""
        distance = source.position.distance(target.position)
        eta = distance / self.params.transporter_speed
        estimated_defense = target.n_ships + target.growth_rate * eta

        fleet_needed = estimated_defense * self.SAFETY_MULTIPLIER
        available = source.n_ships * (1 - self.ATTACK_RESERVE)

        if available >= fleet_needed:
            send = int(min(available, fleet_needed))
            return Action(
                player_id=self.player,
                source_planet_id=source.id,
                destination_planet_id=target.id,
                num_ships=send
            )

        return None

    def get_agent_type(self) -> str:
        return "Defensive Turtle Agent"

if __name__ == "__main__":
    from core.game_state_factory import GameStateFactory

    agent = DefensiveTurtleAgent()
    agent.prepare_to_play_as(Player.Player1, GameParams())
    game_state = GameStateFactory(GameParams()).create_game()
    action = agent.get_action(game_state)
    print(f"Agent: {agent.get_agent_type()}")
    print(f"Action: {action}")