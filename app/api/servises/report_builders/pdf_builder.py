import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from app.api.servises.report_builders import BaseBuilder
from app.utils import logged

__all__ = ["PDFBuilder"]


@logged()
class PDFBuilder(BaseBuilder):
    def write_data(self, data: dict):
        self.log.debug(f"Метод write_data. Записываем данные в файл PDF.")

        file_path = os.path.join(self.folder, self.filename + ".pdf")
        font_path = os.path.abspath(
            os.path.join("app", "api", "static", "Roboto-Regular.ttf")
        )
        pdfmetrics.registerFont(TTFont("Roboto-Regular", font_path))
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        heading_style = styles["Heading1"]
        heading_style.fontName = "Roboto-Regular"

        normal_style = styles["Normal"]
        normal_style.fontName = "Roboto-Regular"

        story.append(Paragraph("ExpensesAccountingBot", heading_style))
        story.append(Spacer(1, 20))

        for period, df in data.items():
            story.append(Paragraph(f"{period}", heading_style))
            story.append(
                Spacer(1, 12)
            )  # 1 - это количество колонок, 12 - размер отступа

            table_data = [df.columns.to_list()] + df.values.tolist()
            total_width = doc.pagesize[0] - 80
            col_width = total_width / len(df.columns)

            table = Table(
                table_data,
                colWidths=[col_width] * len(df.columns),
                splitByRow=True,
                spaceAfter=20,
            )

            table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.Color(0.87, 0.721, 0.529),
                        ),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("FONTNAME", (0, 0), (-1, -1), "Roboto-Regular"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ]
                )
            )

            story.append(table)
            story.append(Spacer(1, 12))

        doc.build(story)
        self.log.debug(f"Метод write_data. Данные записаны в файл {file_path}.")

        return file_path
