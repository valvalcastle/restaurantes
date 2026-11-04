"""Firestore en memoria con solo lo que usa RestaurantRepository.

Permite correr las pruebas sin emulador, sin internet y sin credenciales.
"""
import uuid


class FakeSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return None if self._data is None else dict(self._data)


class FakeDocRef:
    def __init__(self, store, doc_id):
        self._store = store
        self.id = doc_id

    def get(self):
        return FakeSnapshot(self.id, self._store.get(self.id))

    def set(self, data):
        self._store[self.id] = dict(data)

    def update(self, data):
        if self.id not in self._store:
            raise KeyError(f"No existe el documento {self.id}")
        self._store[self.id].update(data)

    def delete(self):
        self._store.pop(self.id, None)


class FakeQuery:
    def __init__(self, store, filters=(), order=None, max_items=None, after=None):
        self._store = store
        self._filters = filters
        self._order = order
        self._max = max_items
        self._after = after

    def _copy(self, **changes):
        params = dict(
            store=self._store, filters=self._filters, order=self._order,
            max_items=self._max, after=self._after,
        )
        params.update(changes)
        return FakeQuery(**params)

    def where(self, *, filter):
        return self._copy(filters=self._filters + (filter,))

    def order_by(self, field, direction="ASCENDING"):
        return self._copy(order=(field, direction))

    def limit(self, count):
        return self._copy(max_items=count)

    def start_after(self, snapshot):
        return self._copy(after=snapshot.id)

    def select(self, _fields):
        return self

    def stream(self):
        rows = [
            (doc_id, data)
            for doc_id, data in self._store.items()
            if all(data.get(f.field_path) == f.value for f in self._filters if f.op_string == "==")
        ]
        if self._order:
            field, direction = self._order
            rows.sort(key=lambda r: (r[1].get(field), r[0]), reverse=direction == "DESCENDING")
        if self._after:
            ids = [r[0] for r in rows]
            if self._after in ids:
                rows = rows[ids.index(self._after) + 1:]
        if self._max is not None:
            rows = rows[: self._max]
        return iter([FakeSnapshot(doc_id, data) for doc_id, data in rows])


class FakeCollection(FakeQuery):
    def document(self, doc_id=None):
        return FakeDocRef(self._store, doc_id or uuid.uuid4().hex[:20])


class FakeFirestore:
    def __init__(self):
        self._collections = {}

    def collection(self, name):
        return FakeCollection(self._collections.setdefault(name, {}))
