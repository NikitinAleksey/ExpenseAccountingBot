import os

from app.api.servises.report_builders import BaseBuilder

from app.utils import logged


__all__ = ["XMLBuilder"]


@logged()
class XMLBuilder(BaseBuilder):
    def write_data(self, data: dict):
        self.log.debug(f"Метод write_data. Записываем данные в файл XML.")
        file_path = os.path.join(self.folder, self.filename + ".xml")

        xml_content = "<?xml version='1.0' encoding='utf-8'?>\n<Reports>\n"

        for period, df in data.items():
            df.columns = df.columns.str.replace(" ", "_")
            xml_content += f"  <!-- Отчет за {period} -->\n"
            xml_content += df.to_xml(
                root_name="Period", row_name="Record", xml_declaration=False
            )

        xml_content += "\n</Reports>"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(xml_content)
        self.log.debug(f"Метод write_data. Данные записаны в файл {file_path}.")

        return file_path
