import time
from multiprocessing import Process, Queue, Lock, Manager
from typing import Any


def test(data: Any, queue: Queue, lock: Lock):

    while True:

        with lock:

            while not queue.empty():
                
                print(queue.get())
                print(data)

        time.sleep(1)



if str(__name__).upper() in ("__MAIN__",):

    with Manager() as manager:

        d: Any = manager.dict()

        queue: Queue = Queue()
        lock: Lock = Lock()

        d["method"] = None
        d["response"] = "say hello!"

        t: Process = Process(target=test, args=(d, queue, lock))

        t.start()

        i: int = 0

        while True:

            with lock:

                queue.put(i)

            i += 1

            time.sleep(1)