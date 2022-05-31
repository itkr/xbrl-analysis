from bs4 import BeautifulSoup
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser


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

    contexts = soup.find_all('xbrli:context')
    for context in contexts:
        print(context.get('id'))
        period = context.find('xbrli:period')
        identifier = context.find('xbrli:entity').find('xbrli:identifier')
        print(f'    {identifier.get("scheme")} {identifier.text}')
        startDate = period.find('xbrli:startdate')
        endDate = period.find('xbrli:enddate')
        instant = period.find('xbrli:instant')
        if startDate and endDate:
            print(f'    {startDate.text} - {endDate.text}')
        if instant:
            print(f'    {instant.text}')

    return


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
    for taxonomy in sorted(get_taxonomy(xbrl_file_path)):
        taxonomy_name = taxonomy.split(':')[1]
        print(taxonomy_name)
        print('  ', len(list(filter(lambda x: x.startswith(taxonomy_name), keys))))

    get_contexts(xbrl_file_path)

    # keys = list(filter(lambda x: x.startswith('jpigp_cor:'), keys))
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
