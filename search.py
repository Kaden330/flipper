from get_info import analyze_car

urls = [
    'https://www.ebay.com/itm/385540746588?hash=item59c404ed5c%3Ag%3APtQAAOSwzgBkNWTH&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
    'https://www.ebay.com/itm/314516664183?hash=item493aa76f77%3Ag%3ANHAAAOSwsF1kIszb&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
    'https://www.ebay.com/itm/325612307278?hash=item4bd001834e%3Ag%3AcmgAAOSwZGtkNG2I&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
    'https://www.ebay.com/itm/166026384440?hash=item26a7f19438%3Ag%3AslYAAOSwPCNkNIQ8&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
]


for url in urls:
    
    print(f'Analyzing car from url: {url}')
    analyze_car(url)
    print('\n\nPrepareing for next car\n\n\n')
