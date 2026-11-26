"""Helpers for Streamlit page tests."""

from html.parser import HTMLParser


def table_rows(app, index=0):
    class Cells(HTMLParser):
        def __init__(self):
            super().__init__()
            self.rows = []
            self.cell = None

        def handle_starttag(self, tag, attrs):
            if tag == "tr":
                self.rows.append([])
            if tag in ("td", "th"):
                self.cell = []

        def handle_data(self, data):
            if self.cell is not None:
                self.cell.append(data)

        def handle_endtag(self, tag):
            if tag in ("td", "th"):
                self.rows[-1].append("".join(self.cell))
                self.cell = None

    tables = [item.proto.body for item in app.get("html") if '<table class="assurance-table"' in item.proto.body]
    parsed = Cells()
    parsed.feed(tables[index])
    headings, *rows = parsed.rows
    return [dict(zip(headings, row)) for row in rows]
