import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Optional, Union

import xmlschema
from bs4 import BeautifulSoup
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser

# xbrl
#     taxonomy
#         keys
#             context
#                 xbrl_data
#                     xbrl_data_value

# TODO: edinet_xbrlを使うのをやめる


# XBRL_DIR = './xbrl_dir'
XBRL_DIR = Path('.', 'xbrl_dir')


@dataclass
class Context:
    context_id: str
    # identifier: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    instant: Optional[str] = None

    def __repr__(self):
        base = f'{self.__class__.__module__}.{self.__class__.__name__} {self.context_id}'
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


# TODO: クラス名
class TaxonomyReference:

    def __init__(self, base_dir, taxonomy_file_path=None):
        self._base_dir = base_dir
        from light_progress.commandline import Loading
        with Loading(0):
            self._load(taxonomy_file_path or self._get_taxonomy_file_path())
        # self._print()

    def _load(self, file_path):
        # TODO: 二重管理解消1
        with Path(file_path).open('r') as f:
            self._soup = BeautifulSoup(f, 'lxml')
        # TODO: 二重管理解消2
        self._xsd = xmlschema.XMLSchema(file_path)

    def _get_taxonomy_file_path(self):
        xsd_files = list(filter(lambda x: x.endswith(
            '.xsd'), os.listdir(self._base_dir)))
        return Path(self._base_dir, xsd_files[0])

    @property
    def imports(self):
        return self._xsd.imports

    @property
    def namespaces(self):
        return self._xsd.namespaces

    def get_linkbaseref(self):
        return [link.get('xlink:href') for link in self._soup.find_all('link:linkbaseref')]

    def get_local_taxonomy_file_paths(self):
        taxonomy_file_paths = filter(
            lambda x: x.endswith('.xml'), os.listdir(self._base_dir))
        taxonomy_file_paths = filter(
            lambda x: not x.startswith('manifest'), taxonomy_file_paths)
        return [Path(self._base_dir, path) for path in taxonomy_file_paths]

    def _print(self):
        # for k, v in self.namespaces.items():
        #     print(f'{k}\t{v}')
        print('---')
        for i in sorted(self.get_local_taxonomy_file_paths()):
            print(i)
        print('---')
        pprint(self._xsd.to_dict(
            sorted(self.get_local_taxonomy_file_paths())[3]))
        print('---')
        for i in sorted(self.get_linkbaseref()):
            print(i)


class Taxonomy:

    taxonomy_dictionary = {
        'jpcrp': '企業内容等の開示に関する内閣府令',
        'jppfs': '日本基準の勘定科目',
        'jpigp': '国際会計基準(IFRS)の勘定科目',
        'jpdei': '文書定義 - 提出文書のメタデータ(提出日付やタイトルなど)を定義するタクソノミ)',
    }

    def __init__(self, taxonomy_name):
        self.name = taxonomy_name

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} {self.name}>'

    @property
    def description(self):
        for key, value in self.__class__.taxonomy_dictionary.items():
            if self.name.startswith(key):
                return value
        return 'unknown'


class XBRL:

    def __init__(self, xbrl_file_path):
        self._load(xbrl_file_path)

    def _load(self, xbrl_file_path):
        # TODO: 二重管理解消 1
        with Path(xbrl_file_path).open('r') as f:
            self.soup = BeautifulSoup(f.read(), 'lxml')
        # TODO: 二重管理解消 2
        self.edinet_xbrl_object = EdinetXbrlParser().parse_file(xbrl_file_path)

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
        return [Taxonomy(taxonomy.split(':')[1])
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

    def make_cash_flow(self, context_ref=None):
        raise

    make_bs = make_balance_sheet
    make_pl = make_profit_and_loss_statement
    make_cf = make_cash_flow


def main():
    xbrl_file_name = list(
        filter(lambda x: x.endswith('.xbrl'), os.listdir(XBRL_DIR)))[0]
    xbrl = XBRL(Path(XBRL_DIR, xbrl_file_name))

    # 利用タクソノミ一覧
    for taxonomy in xbrl.get_taxonomies():
        print(taxonomy, taxonomy.description)
        print(f'  {xbrl.count_keys_by(taxonomy.name)}')

    t = TaxonomyReference(XBRL_DIR)
    print(t)

    # コンテキスト一覧
    # for context in xbrl.get_contexts():
    #     print(context)

    # 例
    # xbrl.get_data_by(taxonomy='jpdei', context_ref='context')

    # 値の表示
    # xbrl.print_values()
    # xbrl.print_values('jppfs')


if __name__ == '__main__':
    main()
