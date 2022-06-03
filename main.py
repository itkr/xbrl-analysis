from dataclasses import dataclass
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


def get_taxonomy(xbrl_file_path):
    with open(xbrl_file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    xbrli = soup.find('xbrli:xbrl')
    return list(xbrli.attrs)


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
            contexts.append(Context(context_id, startDate=startDate.text, endDate=endDate.text))
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


def load():
    parser = EdinetXbrlParser()
    xbrl_file_path = 'public.xbrl'
    edinet_xbrl_object = parser.parse_file(xbrl_file_path)

    keys = edinet_xbrl_object.get_keys()

    # 利用タクソノミ一覧
    for taxonomy in sorted(get_taxonomy(xbrl_file_path)):
        taxonomy_name = taxonomy.split(':')[1]
        # print(taxonomy)
        print(taxonomy_name)
        if taxonomy_name.startswith('jpcrp'):
            print('企業内容等の開示に関する内閣府令')
        if taxonomy_name.startswith('jppfs'):
            print('日本基準の勘定科目')
        if taxonomy_name.startswith('jpigp'):
            print('国際会計基準(IFRS)の勘定科目')
        if taxonomy_name.startswith('jpdei'):
            print('文書定義 - 提出文書のメタデータ(提出日付やタイトルなど)を定義するタクソノミ')
        print(f'  {len(list(filter(lambda x: x.startswith(taxonomy_name), keys)))}')

    # コンテキスト一覧
    # contexts = get_contexts(xbrl_file_path)
    # for context in contexts:
        # print(context)

    # link 6
    # xbrldi 1
    # xbrli 14
    keys = list(filter(lambda x: x.startswith('xbrldi:'), keys))
    for key in keys:
        print(key)
        data_list = edinet_xbrl_object.get_data_list(key)
        for data in data_list:
            # int(data.get_value())
            value = '[HTML]' if is_html(data.get_value()) else data.get_value()
            print(
                f'    {data.get_context_ref()} {value} {data.get_unit_ref()} {data.get_decimals()}')


def main():
    load()


if __name__ == '__main__':
    main()
