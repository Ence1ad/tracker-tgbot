import datetime

year = datetime.datetime.today().isocalendar().year
week = datetime.datetime.today().isocalendar().week

d = f"{year}-W{week}"
monday = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w").date()
sunday = monday + datetime.timedelta(days=6)
current_week_data = f"{monday} - {sunday}"


new_sheet_name = datetime.datetime.today().isocalendar().week
