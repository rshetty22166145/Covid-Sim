from typing import Any


class AbstractQueue:
    def __init__(self) -> None:
        """Initialize new Queue"""

    def is_empty(self) -> bool:
        """Return if queue is empty"""
        raise NotImplementedError

    def enqueue(self, item: Any) -> None:
        """Add item to queue"""
        raise NotImplementedError

    def dequeue(self) -> Any:
        """Remove item from queue and return it"""
        raise NotImplementedError

    def peek(self) -> Any:
        """Get the next item to be removed from the queue without removing it"""
        raise NotImplementedError


class Queue(AbstractQueue):

    def __init__(self):
        AbstractQueue.__init__(self)

        # Tracks id of next item being added
        self.__current_id = 0
        # Tracks id of item to be dequeued next
        self.__dequeue_id = 0
        self.__items = {}

    def enqueue(self, item: Any) -> None:
        # Adds item with current_id as key
        self.__items[self.__current_id] = item
        # Increments id
        self.__current_id += 1

    def dequeue(self) -> Any:
        if self.is_empty():
            raise EmptyQueueError
        else:
            # Gets item, removes item, increments dequeue count
            itm = self.__items[self.__dequeue_id]
            # pop() for dict is O(1) with a worst case O(N).
            # This should be slightly more efficient than a list-based queue
            self.__items.pop(self.__dequeue_id)
            self.__dequeue_id += 1
        return itm

    def peek(self) -> Any:
        if self.is_empty():
            raise EmptyQueueError
        else:
            # Get first item in the queue
            return self.__items[self.__dequeue_id]

    def is_empty(self) -> bool:
        return len(self.__items) == 0


class EmptyQueueError(Exception):
    def __str__(self) -> str:
        return "dequeue or peek may not be called on an empty queue"
