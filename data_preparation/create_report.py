from openpyxl.chart.marker import DataPoint
from openpyxl.drawing.colors import SchemeColor
from openpyxl.worksheet.worksheet import Worksheet
from pandas import DataFrame
from copy import deepcopy

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference, PieChart
from openpyxl.utils.dataframe import dataframe_to_rows

from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.fill import GradientFillProperties, GradientStop

from data_preparation.datetime_data import new_sheet_name, current_week_data
from tgbot.utils.answer_text import xlsx_title


async def create_fig(df_action: DataFrame, df_categories: DataFrame, sheet_name: str = xlsx_title) -> None:
    wb: Workbook = Workbook()
    create_bar_charts(df=df_action, wb=wb)
    create_pie_chart(df=df_categories, wb=wb)
    wb.save(sheet_name)


def create_bar_charts(*, df: DataFrame, wb: Workbook) -> None:
    ws: Worksheet = wb.active
    ws.title = f"bars(week - {new_sheet_name})"
    for row in dataframe_to_rows(df, index=True, header=True):
        ws.append(row)
    ws.delete_rows(2)
    ws['A1'] = "dow/actions"
    ws.column_dimensions["A"].width = 14
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = cell.alignment.copy(wrapText=True)
    chart = BarChart()
    chart.y_axis.title = 'Devoted time'
    chart.x_axis.title = 'Days of the week'

    data = Reference(ws, min_col=2, min_row=1, max_row=8, max_col=len(df.columns) + 1)
    cats = Reference(ws, min_col=1, min_row=2, max_row=8)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.shape = 6
    simple_stack_chart(chart, ws)
    horizontal_bar_chart(chart, ws)
    stacked_chart(chart, ws)
    percent_stacked_chart(chart, ws)


def simple_stack_chart(chart: BarChart, ws: Worksheet) -> None:
    chart1 = deepcopy(chart)
    chart1.type = "col"
    chart1.style = 10
    chart1.title = current_week_data
    ws.add_chart(chart1, "A10")


def horizontal_bar_chart(chart: BarChart, ws: Worksheet) -> None:
    chart2 = deepcopy(chart)
    chart2.style = 10
    chart2.type = "bar"
    chart2.title = current_week_data
    ws.add_chart(chart2, "K10")


#
def stacked_chart(chart: BarChart, ws: Worksheet) -> None:
    chart3 = deepcopy(chart)
    chart3.type = "col"
    chart3.style = 10
    chart3.grouping = "stacked"
    chart3.overlap = 100
    chart3.title = current_week_data
    ws.add_chart(chart3, "A27")


def percent_stacked_chart(chart: BarChart, ws: Worksheet) -> None:
    chart4 = deepcopy(chart)
    chart4.type = "bar"
    chart4.style = 10
    chart4.grouping = "percentStacked"
    chart4.overlap = 100
    chart4.title = current_week_data
    ws.add_chart(chart4, "K27")


def create_pie_chart(*, df: DataFrame, wb: Workbook) -> None:
    ws: Worksheet = wb.create_sheet(title=f"pie(week - {new_sheet_name})")
    for row in dataframe_to_rows(df, index=True, header=True):
        ws.append(row)
    ws.delete_rows(2)
    ws['A1'] = "quantity"
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 10
    pie = PieChart()
    labels = Reference(ws, min_col=2, min_row=2, max_row=len(df) + 1, max_col=3)
    data = Reference(ws, min_col=1, min_row=1, max_row=len(df) + 1)
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(labels)
    pie.title = "Amount of time spent by category"
    gradient_pie(pie, ws)


def gradient_pie(pie: PieChart, ws: Worksheet) -> None:
    # Cut the first slice out of the pie and apply a gradient to it
    slice_ = DataPoint(idx=0, explosion=20, spPr=GraphicalProperties(
        gradFill=GradientFillProperties(
            gsLst=(
                GradientStop(
                    pos=0,
                    prstClr='blue'
                ),
                GradientStop(
                    pos=100000,
                    schemeClr=SchemeColor(
                        val='accent1',
                        lumMod=30000,
                        lumOff=70000
                    )
                )
            )
        )
    )
                      )
    pie.series[0].data_points = [slice_]
    ws.add_chart(pie, "E1")
