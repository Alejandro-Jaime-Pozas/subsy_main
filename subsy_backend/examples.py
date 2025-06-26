# ls = [
#     {"id": 1, "name": "Alice", "age": 28, "city": "New York"},
#     {"id": 2, "name": "Bob", "age": 34, "city": "Los Angeles"},
#     {"id": 3, "name": "Charlie", "age": 25, "city": "Chicago"},
# ]

# filter_keys = {"name", "city"}
# filtered = list(map(lambda p: {k: v for k, v in p.items() if k in filter_keys}, ls))
# hard_coded = [{"name": p["name"], "city": p["city"]} for p in ls]
# # print(filtered)
# # print(hard_coded)

# # from datetime import datetime, timezone

# # current_utc_date = datetime.now(timezone.utc).date()
# # current_date = datetime.now(timezone.utc)
# # print(current_utc_date)
# # print(current_date)

# new = []
# for p in ls:
#     new_p = {}
#     for k in filter_keys:
#         new_p[k] = p[k]  # if this works, then if val doesn't exist in dict acts diff than when val does exists in dict...
#     new.append(new_p)
# print(new)

# transactions = [{k: tx[k] for k in filter_keys} for tx in ls]
# print(transactions)


