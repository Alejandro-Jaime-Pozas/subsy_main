from datetime import datetime, timezone

current_utc_date = datetime.now(timezone.utc).date()
print(current_utc_date)
