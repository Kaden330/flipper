from get_info import analyze_car
from datetime import datetime
from tqdm import tqdm
from page import Page, StyledPage

def main():
    urls = [
        'https://www.ebay.com/itm/314516664183?hash=item493aa76f77%3Ag%3ANHAAAOSwsF1kIszb&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
        'https://www.ebay.com/itm/325612307278?hash=item4bd001834e%3Ag%3AcmgAAOSwZGtkNG2I&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
        'https://www.ebay.com/itm/166026384440?hash=item26a7f19438%3Ag%3AslYAAOSwPCNkNIQ8&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
    ]

    long_breif = Page()
    long_breif_styled = StyledPage()
    long_breif_styled.h1('Flipper Search Results')

    start = datetime.now()
    for url in tqdm(urls):
        #try:
        result = analyze_car(url)
        long_breif.press(result, end='\n\n')
        long_breif_styled.add_raw_text(result, end='\n')

        #except Exception as e:
        #    print(e)

        long_breif.press('Preparing for next car...', end='\n\n')

    time = datetime.now() - start
    avg = time/len(urls)

    print(f'average time: {avg}')

    with open('long_breifing.txt' , 'w') as file:
        file.write(long_breif.body)

    with open('styled_breifing.md' , 'w') as file:
        file.write(long_breif_styled.body)

if __name__ == '__main__':
    main()