from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser


@dataclass
class Context:
    context_id: str
    # identifier: str
    # startDate: str | None = None
    # endDate: str | None = None
    # instant: str | None = None
    startDate: str = None
    endDate: str = None
    instant: str = None


def get_taxonomy_names(xbrl_file_path):
    with open(xbrl_file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    return [taxonomy.split(':')[1] for taxonomy in list(soup.find('xbrli:xbrl').attrs)]


def get_contexts(xbrl_file_path):
    # <xbrli:context id="Prior4YearDuration">
    #   <xbrli:entity>
    #     <xbrli:identifier scheme="http://disclosure.edinet-fsa.go.jp">E04837-000</xbrli:identifier>
    #   </xbrli:entity>
    #   <xbrli:period>
    #     <xbrli:startDate>2016-04-01</xbrli:startDate>
    #     <xbrli:endDate>2017-03-31</xbrli:endDate>
    #   </xbrli:period>
    # </xbrli:context>
    with open(xbrl_file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    contexts = []
    for context in soup.find_all('xbrli:context'):
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


def is_html(value):
    # intなど
    if not isinstance(value, str):
        return False
    soup = BeautifulSoup(value, 'lxml')
    # 空文字など
    if not soup.html:
        return False
    # タグ無し文字
    return soup.html.body.p.text != value


def is_number(value):
    try:
        int(value)
        return True
    except Exception:
        return False


def is_boolean_text(value):
    return value in ['true', 'false']


def is_date_text(value):
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def convert_value(taxonomy_name: str, key: str, value):
    # TODO: タクソノミ定義をもとにコンバート
    if not value:
        return value
    if is_html(value):
        # return BeautifulSoup(value, 'lxml').prettify()
        return '[HTML]'
    if is_number(value):
        return float(value) if '.' in value else int(value)
    if is_boolean_text(value):
        return True if value == 'true' else False
    if is_date_text(value):
        return datetime.strptime(value, '%Y-%m-%d').date()
    return value


def print_xbrl_values(edinet_xbrl_object, prefix=None):
    keys = edinet_xbrl_object.get_keys()
    if prefix:
        keys = list(filter(lambda x: x.startswith(prefix), keys))
    for key in keys:
        print(key)
        data_list = edinet_xbrl_object.get_data_list(key, auto_lower=False)
        for data in data_list:
            value = convert_value(key.split(':')[0], key, data.get_value())
            print(
                f'    {data.get_context_ref()} {value} {data.get_unit_ref()} {data.get_decimals()}')


taxonomy_dictionary = {
    'jpcrp': '企業内容等の開示に関する内閣府令',
    'jppfs': '日本基準の勘定科目',
    'jpigp': '国際会計基準(IFRS)の勘定科目',
    'jpdei': '文書定義 - 提出文書のメタデータ(提出日付やタイトルなど)を定義するタクソノミ)',
}


def get_taxonomy_description(taxonomy_name):
    for key, value in taxonomy_dictionary.items():
        if taxonomy_name.startswith(key):
            return value
    return ''


def load():
    parser = EdinetXbrlParser()
    xbrl_file_path = 'public.xbrl'
    edinet_xbrl_object = parser.parse_file(xbrl_file_path)

    keys = edinet_xbrl_object.get_keys()

    # 利用タクソノミ一覧
    for taxonomy in sorted(get_taxonomy_names(xbrl_file_path)):
        print(taxonomy, get_taxonomy_description(taxonomy))
        print(f'  {len(list(filter(lambda x: x.startswith(taxonomy), keys)))}')

    # コンテキスト一覧
    # contexts = get_contexts(xbrl_file_path)
    # for context in contexts:
        # print(context)

    # print_xbrl_values(edinet_xbrl_object)
    print_xbrl_values(edinet_xbrl_object, 'jpdei_cor')


def main():
    load()


if __name__ == '__main__':
    main()
