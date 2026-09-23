from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from app.services.video_store import InMemoryVideoStore


def test_only_one_concurrent_request_queues_analysis(tmp_path):
    store = InMemoryVideoStore(tmp_path / "uploads", tmp_path / "outputs")
    record = store.create("clip.mp4")
    barrier = Barrier(2)

    def queue():
        barrier.wait()
        return store.queue_for_analysis(record.video_id)[1]

    with ThreadPoolExecutor(max_workers=2) as executor:
        scheduled = list(executor.map(lambda _: queue(), range(2)))

    assert sorted(scheduled) == [False, True]
    assert record.status == "queued"
