from collections import UserList


class CommandHistory(UserList):
    """A simple list to store command history."""

    def add(self, command: str):
        """Add a command to the history if it's not empty and not a duplicate of the last."""
        command = command.strip()
        if command and (not self.data or command != self.data[-1]):
            self.data.append(command)

    def get_previous(self, index: int) -> str:
        """Get the previous command based on the current index."""
        if 0 <= index < len(self.data):
            return self.data[index]
        return ''

    def get_next(self, index: int) -> str:
        """Get the next command based on the current index."""
        if 0 <= index < len(self.data):
            return self.data[index]
        return ''
