from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from bs4 import BeautifulSoup
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser

# xbrl
#     taxonomy
#         keys
#             context
#                 xbrl_data
#                     xbrl_data_value

# TODO: edinet_xbrlを使うのをやめる


@dataclass
class Context:
    context_id: str
    # identifier: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    instant: Optional[str] = None

    def __repr__(self):
        base = f'{self.__class__.__name__} {self.context_id}'
        if self.startDate:
            return f'<{base} start={self.startDate} end={self.endDate}>'
        elif self.instant:
            return f'<{base} instant={self.instant}>'
        return f'<{base}>'


@dataclass
class XbrlData:
    taxonomy_name: str
    context_ref: str  # Contextがたにする
    decimals: int
    key_name: str
    unit_ref: int
    value: Union[None, bool, int, float, str, BeautifulSoup]

    def __repr__(self):
        return f'    {self.context_ref} {self.value} {self.unit_ref} {self.decimals}'


class XBRLDataValueConverter:

    @classmethod
    def convert_value(cls, taxonomy_name: str, key_name: str, value) -> Union[
            float, int, str, bool, None, BeautifulSoup]:
        # TODO: タクソノミ定義をもとにコンバート
        if not value:
            return value
        if cls.is_html(value):
            # return BeautifulSoup(value, 'lxml').prettify()
            return '[HTML]'
        if cls.is_number(value):
            return float(value) if '.' in value else int(value)
        if cls.is_boolean_text(value):
            return True if value == 'true' else False
        if cls.is_date_text(value):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value

    @classmethod
    def is_html(cls, value):
        # intなど
        if not isinstance(value, str):
            return False
        soup = BeautifulSoup(value, 'lxml')
        # 空文字など
        if not soup.html:
            return False
        # タグ無し文字
        return soup.html.body.p.text != value

    @classmethod
    def is_number(cls, value):
        try:
            int(value)
            return True
        except Exception:
            return False

    @classmethod
    def is_boolean_text(cls, value):
        return value in ['true', 'false']

    @classmethod
    def is_date_text(cls, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False


class Taxonomy:

    taxonomy_dictionary = {
        'jpcrp': '企業内容等の開示に関する内閣府令',
        'jppfs': '日本基準の勘定科目',
        'jpigp': '国際会計基準(IFRS)の勘定科目',
        'jpdei': '文書定義 - 提出文書のメタデータ(提出日付やタイトルなど)を定義するタクソノミ)',
    }

    @classmethod
    def get_description(cls, taxonomy_name):
        for key, value in cls.taxonomy_dictionary.items():
            if taxonomy_name.startswith(key):
                return value
        return ''


class XBRL:

    def __init__(self, xbrl_file_path):
        self.xbrl_file_path = xbrl_file_path
        self.load()

    def load(self):
        # TODO: 二重管理解消 1
        with open(self.xbrl_file_path, 'r') as f:
            self.soup = BeautifulSoup(f.read(), 'lxml')
        # TODO: 二重管理解消 2
        self.edinet_xbrl_object = EdinetXbrlParser().parse_file(self.xbrl_file_path)

    def print_values(self, prefix=None):
        result = {}
        for key in self.get_keys_by(prefix):
            data_list = self.edinet_xbrl_object.get_data_list(
                key, auto_lower=False)
            try:
                taxonomy_name, key_name = key.split(':')
            except ValueError:
                # 'html', 'body' が入ってくる
                continue

            if taxonomy_name not in result.keys():
                result[taxonomy_name] = []

            print(key)
            # TODO: これだとkeyの改装を無視してtaxonomyごとにdataを入れてしまっている。これでいいか？
            result[taxonomy_name] = [XbrlData(
                context_ref=data.get_context_ref(),
                decimals=data.get_decimals(),
                key_name=key_name,
                taxonomy_name=taxonomy_name,
                value=XBRLDataValueConverter.convert_value(
                    taxonomy_name, key_name, data.get_value()),
                unit_ref=data.get_unit_ref()) for data in data_list]
            for v in result[taxonomy_name]:
                print(v)

        return result

    def get_taxonomies(self):
        # TODO: 実装
        raise

    def get_taxonomy_names(self):
        return [taxonomy.split(':')[1]
                for taxonomy in list(self.soup.find('xbrli:xbrl').attrs)]

    def get_contexts(self):
        # <xbrli:context id="Prior4YearDuration">
        #   <xbrli:entity>
        #     <xbrli:identifier scheme="http://disclosure.edinet-fsa.go.jp">E04837-000</xbrli:identifier>
        #   </xbrli:entity>
        #   <xbrli:period>
        #     <xbrli:startDate>2016-04-01</xbrli:startDate>
        #     <xbrli:endDate>2017-03-31</xbrli:endDate>
        #   </xbrli:period>
        # </xbrli:context>
        contexts = []
        for context in self.soup.find_all('xbrli:context'):
            period = context.find('xbrli:period')
            startDate = period.find('xbrli:startdate')
            endDate = period.find('xbrli:enddate')
            instant = period.find('xbrli:instant')
            context_id = context.get('id')
            if startDate and endDate:
                contexts.append(
                    Context(context_id, startDate=startDate.text, endDate=endDate.text))
            elif instant:
                contexts.append(Context(context_id, instant=instant.text))
            else:
                raise ValueError
        return contexts

    def count_keys_by(self, taxonomy_name=None):
        return len(list(self.get_keys_by(taxonomy_name)))

    def get_keys_by(self, taxonomy_name=None):
        prefix = taxonomy_name
        keys = self.edinet_xbrl_object.get_keys()
        if prefix:
            return list(filter(lambda x: x.startswith(prefix), keys))
        return keys

    def get_data_by(self, **kwargs):
        # by taxonomy
        # by key
        raise

    def to_csv(self):
        raise

    def to_pandas(self):
        raise

    def make_balance_sheet(self, context_ref=None):
        raise

    def make_profit_and_loss_statement(self, context_ref=None):
        raise


def main():
    xbrl = XBRL('public.xbrl')

    # 利用タクソノミ一覧
    for taxonomy_name in sorted(xbrl.get_taxonomy_names()):
        print(taxonomy_name, Taxonomy.get_description(taxonomy_name))
        print(f'  {xbrl.count_keys_by(taxonomy_name)}')

    # コンテキスト一覧
    contexts = xbrl.get_contexts()
    for context in contexts:
        print(context)

    # xbrl.get_data_by(taxonomy='jpdei', context_ref='context')

    # 値の表示
    # xbrl.print_values()
    xbrl.print_values('jpdei_cor')


if __name__ == '__main__':
    main()
