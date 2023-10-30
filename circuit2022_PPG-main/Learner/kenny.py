from datetime import date

from Learner import models

import yaml



def kenn():
    first = models.keyword_URL(keyword_text = "1st", individual_URL = "b", date_scraped=date.today(), score = "5")
    second = models.keyword_URL(keyword_text = "2nd", individual_URL = "b", date_scraped=date.today(), score = "10")
    third = models.keyword_URL(keyword_text = "3rd", individual_URL = "b", date_scraped=date.today(), score = "15")

    print(first.keyword_text)

    all_data = models.keyword_URL.objects.all()
    for item in all_data:
        print(item)

    data = dict(
        A = 'a',
        B = dict(
            C = 'c',
            D = 'd',
            E = 'e',
        )
    )

    with open('data.yml', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)







