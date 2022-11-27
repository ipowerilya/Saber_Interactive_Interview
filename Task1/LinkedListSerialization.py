# python 3.9
from __future__ import annotations

from io import BufferedWriter, BufferedReader
from typing import Iterator, IO

INT_SIZE_BYTES = 4
NULL = b"\x00"


def main():
    a = ListNode("A")
    b = ListNode("BB", p=a)
    c = ListNode("CCC", p=b)
    d = ListNode("DDDD", p=c)
    e = ListNode("", p=d)

    a.next = b
    a.rand = e
    b.next = c
    c.next = d
    c.rand = c
    d.next = e

    l0 = ListRand(head=a, tail=e, count=5)
    print_list(l0)
    with open("list.bin", "wb") as file:
        l0.serialize(BufferedWriter(file))

    print("-----------------")

    l1 = ListRand()
    with open("list.bin", "rb") as file:
        l1.deserialize(BufferedReader(file))
    print_list(l1)

    #                       HEX dump of saved file
    #            00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
    #
    # 00000000   41 00 00 00 00 04 42 42 00 FF FF FF FF 43 43 43  A.....BB.....CCC
    # 00000010   00 00 00 00 02 44 44 44 44 00 FF FF FF FF 00 FF  .....DDDD.......
    # 00000020   FF FF FF                                         ...
    #                       Result
    # prev='None' data='A' next='BB' rand=''
    # prev='A' data='BB' next='CCC' rand='None'
    # prev='BB' data='CCC' next='DDDD' rand='CCC'
    # prev='CCC' data='DDDD' next='' rand='None'
    # prev='DDDD' data='' next='None' rand='None'
    # -----------------
    # prev='None' data='A' next='BB' rand=''
    # prev='A' data='BB' next='CCC' rand='None'
    # prev='BB' data='CCC' next='DDDD' rand='CCC'
    # prev='CCC' data='DDDD' next='' rand='None'
    # prev='DDDD' data='' next='None' rand='None'


class ListNode:
    def __init__(self, data: str, p: ListNode = None, n: ListNode = None, r: ListNode = None):
        self.prev = p
        self.next = n
        self.rand = r
        self.data = data


class ListRand:
    def __init__(self, head: ListNode = None, tail: ListNode = None, count: int = 0):
        self.head = head
        self.tail = tail
        self.count = count

    def serialize(self, stream: IO[bytes]):
        # Create map Node-Node_index for list
        index_by_node = {}
        for index, node in enumerate(self._iter_nodes()):
            index_by_node[node] = index

        # Write node data and random node index to file
        for node in self._iter_nodes():
            write_str(stream, node.data)
            write_int(stream, index_by_node.get(node.rand, -1))

    def deserialize(self, stream: IO[bytes]):
        nodes = []
        rand_indexes = []
        # Iterate through stream and write nodes and indexes to list
        for data, rand_idx in self._iter_stream(stream):
            nodes.append(ListNode(data=data))
            rand_indexes.append(rand_idx)

        self.count = len(nodes)
        if not self.count:
            return

        self.head = nodes[0]
        self.tail = nodes[-1]
        # Iterate through created lists and place correct random node references
        for idx, rand_idx in enumerate(rand_indexes):
            if rand_idx != -1:
                nodes[idx].rand = nodes[rand_idx]
        # Link nodes to nodes
        for idx, node in enumerate(nodes[1:], start=1):
            node.prev = nodes[idx - 1]
            node.prev.next = node

    def _iter_nodes(self) -> Iterator[ListNode]:
        n = self.head
        while n:
            yield n
            n = n.next

    @staticmethod
    def _iter_stream(stream: IO[bytes]) -> Iterator[tuple[str, int]]:
        while True:
            data = read_str(stream)
            if data is None:
                break
            yield data, read_int(stream)


def write_int(stream: IO[bytes], x: int):
    stream.write(x.to_bytes(INT_SIZE_BYTES, "big", signed=True))


def write_str(stream: IO[bytes], s: str):
    stream.write(s.encode())
    stream.write(NULL)


def read_int(stream: IO[bytes]) -> int | None:
    data = stream.read(INT_SIZE_BYTES)
    if not data:
        return None
    return int.from_bytes(data, "big", signed=True)


def read_str(stream: IO[bytes]) -> str | None:
    buf = []
    while True:
        ch = stream.read(1)
        if ch == b"":
            break
        buf.append(ch)
        if ch == NULL:
            break
    if not buf:
        return None
    return b''.join(buf[:-1]).decode()


def print_list(l: ListRand):
    for node in l._iter_nodes():
        print(f"prev='{node.prev and node.prev.data}'"
              f" data='{node.data}'"
              f" next='{node.next and node.next.data}'"
              f" rand='{node.rand and node.rand.data}'")


main()
