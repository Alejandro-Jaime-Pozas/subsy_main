from datetime import datetime, timezone

current_utc_date = datetime.now(timezone.utc).date()
current_date = datetime.now(timezone.utc)
print(current_utc_date)
print(current_date)
