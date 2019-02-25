import enum

from pazaak.helpers.bases import SerializableEnum


@enum.unique
class Turn(SerializableEnum):
    PLAYER = 'player'
    OPPONENT = 'opponent'

    @classmethod
    def opposite_turn(cls, turn) -> 'Turn':
        """
        Given a turn, returns the opposite player's Turn enum.
        """
        switch = {
            cls.PLAYER: cls.OPPONENT,
            cls.OPPONENT: cls.PLAYER
        }
        if turn not in switch:
            raise ValueError('{0} is not a valid Turn'.format(turn))
        return switch[turn]

    def key(self) -> str:
        return self.value