import os
from io import BytesIO

import pandas as pd

from app.api.servises.report_builders import BaseBuilder


__all__ = ['XLSBuilder']


class XLSBuilder(BaseBuilder):
    def write_data(self):
        file_path = os.path.join(self.folder, self.filename + '.xlsx')
        self.data_frame.to_excel(file_path, index=False)
        return file_path

    def generate_report(self):
        self.data_frame['Процент использования'] = self.data_frame.apply(
            lambda row: round((row['Сумма затрат'] / row['Лимит'] * 100)) if row['Лимит'] > 0 else 0,
            axis=1
        ).astype(int)
        file_path = self.write_data()

        return file_path
