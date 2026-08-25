import datetime
import json
from typing import Any, List, Optional, Type
from pymongo import MongoClient
from app.config import settings

class MongoSession:
    """
    High-performance MongoDB Session Adapter providing SQLAlchemy-compatible
    query and persistence interface for MongoDB Atlas.
    """
    def __init__(self, client: MongoClient, db_name: str = "career_agentic_ai"):
        self.client = client
        self.db = client[db_name]
        self._new_objects = []
        self._dirty_objects = []
        self._deleted_objects = []

    def get_next_id(self, sequence_name: str) -> int:
        counter = self.db.counters.find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return counter.get("seq", 1)

    def query(self, model_cls: Type) -> 'MongoQuery':
        return MongoQuery(self, model_cls)

    def add(self, obj: Any):
        if obj not in self._new_objects:
            self._new_objects.append(obj)

    def delete(self, obj: Any):
        if obj not in self._deleted_objects:
            self._deleted_objects.append(obj)

    def commit(self):
        # 1. Process deletions
        for obj in self._deleted_objects:
            table_name = getattr(obj, "__tablename__", type(obj).__name__.lower())
            pk_name = self._get_pk_name(obj)
            pk_val = getattr(obj, pk_name, None)
            if pk_val is not None:
                self.db[table_name].delete_one({pk_name: pk_val})
        self._deleted_objects.clear()

        # 2. Process new objects
        for obj in self._new_objects:
            table_name = getattr(obj, "__tablename__", type(obj).__name__.lower())
            pk_name = self._get_pk_name(obj)
            pk_val = getattr(obj, pk_name, None)
            
            if pk_val is None or pk_val == 0:
                pk_val = self.get_next_id(table_name)
                setattr(obj, pk_name, pk_val)

            doc = self._model_to_dict(obj)
            self.db[table_name].update_one({pk_name: pk_val}, {"$set": doc}, upsert=True)
        self._new_objects.clear()

        # 3. Process updates / dirty objects in query cache
        for obj in self._dirty_objects:
            table_name = getattr(obj, "__tablename__", type(obj).__name__.lower())
            pk_name = self._get_pk_name(obj)
            pk_val = getattr(obj, pk_name, None)
            if pk_val is not None:
                doc = self._model_to_dict(obj)
                self.db[table_name].update_one({pk_name: pk_val}, {"$set": doc}, upsert=True)
        self._dirty_objects.clear()

    def refresh(self, obj: Any):
        table_name = getattr(obj, "__tablename__", type(obj).__name__.lower())
        pk_name = self._get_pk_name(obj)
        pk_val = getattr(obj, pk_name, None)
        if pk_val is not None:
            doc = self.db[table_name].find_one({pk_name: pk_val})
            if doc:
                self._dict_to_model(doc, obj)

    def close(self):
        pass

    def _get_pk_name(self, obj: Any) -> str:
        t = getattr(obj, "__tablename__", "")
        if t == "users": return "user_id"
        if t == "jobs": return "job_id"
        if t == "applications": return "application_id"
        if t == "interview_sessions": return "session_id"
        return "id"

    def _model_to_dict(self, obj: Any) -> dict:
        data = {}
        for k, v in obj.__dict__.items():
            if not k.startswith("_") and not callable(v):
                # Relationships shouldn't be serialized directly
                if k in ["user", "job", "applications", "interview_sessions"]:
                    continue
                data[k] = v
        return data

    def _dict_to_model(self, doc: dict, obj: Any):
        for k, v in doc.items():
            if k != "_id" and hasattr(obj, k):
                setattr(obj, k, v)


class MongoQuery:
    def __init__(self, session: MongoSession, model_cls: Type):
        self.session = session
        self.model_cls = model_cls
        self.table_name = getattr(model_cls, "__tablename__", model_cls.__name__.lower())
        self.collection = session.db[self.table_name]
        self._filters = []
        self._sort_field = None
        self._sort_dir = 1
        self._limit_num = None

    def filter(self, *criteria) -> 'MongoQuery':
        for c in criteria:
            self._filters.append(c)
        return self

    def order_by(self, *args) -> 'MongoQuery':
        # E.g. Job.posted_at.desc() or Application.updated_at.desc()
        if args:
            arg = args[0]
            desc = getattr(arg, "is_desc", False) or "desc" in str(arg).lower()
            field_name = getattr(arg, "name", str(arg).split(".")[-1].replace("()", "").replace("desc", "").strip())
            self._sort_field = field_name
            self._sort_dir = -1 if desc else 1
        return self

    def limit(self, num: int) -> 'MongoQuery':
        self._limit_num = num
        return self

    def count(self) -> int:
        mongo_filter = self._build_mongo_filter()
        return self.collection.count_documents(mongo_filter)

    def first(self) -> Optional[Any]:
        results = self.limit(1).all()
        return results[0] if results else None

    def all(self) -> List[Any]:
        mongo_filter = self._build_mongo_filter()
        cursor = self.collection.find(mongo_filter)
        
        if self._sort_field:
            cursor = cursor.sort(self._sort_field, self._sort_dir)
        if self._limit_num:
            cursor = cursor.limit(self._limit_num)

        objs = []
        for doc in cursor:
            obj = self.model_cls()
            for k, v in doc.items():
                if k != "_id" and hasattr(obj, k):
                    setattr(obj, k, v)
            
            # Attach relationships if needed
            self._populate_relationships(obj)
            
            self.session._dirty_objects.append(obj)
            objs.append(obj)
        return objs

    def _populate_relationships(self, obj: Any):
        t = self.table_name
        if t == "applications":
            job_id = getattr(obj, "job_id", None)
            if job_id:
                job_doc = self.session.db["jobs"].find_one({"job_id": job_id})
                if job_doc:
                    from app.models import Job
                    job_obj = Job()
                    for k, v in job_doc.items():
                        if k != "_id" and hasattr(job_obj, k):
                            setattr(job_obj, k, v)
                    obj.job = job_obj
            user_id = getattr(obj, "user_id", None)
            if user_id:
                user_doc = self.session.db["users"].find_one({"user_id": user_id})
                if user_doc:
                    from app.models import User
                    user_obj = User()
                    for k, v in user_doc.items():
                        if k != "_id" and hasattr(user_obj, k):
                            setattr(user_obj, k, v)
                    obj.user = user_obj

    def _build_mongo_filter(self) -> dict:
        if not self._filters:
            return {}

        and_clauses = []
        for crit in self._filters:
            # Check for binary expressions (e.g. User.email == val, Job.job_type == val)
            crit_str = str(crit)
            
            # SQLAlchemy BinaryExpression inspection
            if hasattr(crit, "left") and hasattr(crit, "right"):
                col_name = getattr(crit.left, "name", str(crit.left).split(".")[-1])
                val = getattr(crit.right, "value", None)
                if val is None:
                    # Try evaluate right side
                    try:
                        val = crit.right.element.value
                    except Exception:
                        val = getattr(crit.right, "val", None)

                op_name = getattr(crit, "operator", None)
                op_str = str(op_name) if op_name else ""

                if "like" in op_str.lower() or "ilike" in op_str.lower():
                    # Handle %wildcard%
                    clean_pattern = str(val).strip("%")
                    and_clauses.append({col_name: {"$regex": clean_pattern, "$options": "i"}})
                elif "is" in op_str.lower() or "=" in op_str:
                    and_clauses.append({col_name: val})
                else:
                    and_clauses.append({col_name: val})
            elif "or(" in crit_str.lower() or hasattr(crit, "clauses"):
                # Handle or_() filter clauses
                or_sub = []
                clauses = getattr(crit, "clauses", [])
                for sub in clauses:
                    if hasattr(sub, "left") and hasattr(sub, "right"):
                        c_name = getattr(sub.left, "name", str(sub.left).split(".")[-1])
                        c_val = getattr(sub.right, "value", str(sub.right).strip("%'"))
                        clean_pattern = str(c_val).strip("%")
                        or_sub.append({c_name: {"$regex": clean_pattern, "$options": "i"}})
                if or_sub:
                    and_clauses.append({"$or": or_sub})
            else:
                pass

        if not and_clauses:
            return {}
        if len(and_clauses) == 1:
            return and_clauses[0]
        return {"$and": and_clauses}
