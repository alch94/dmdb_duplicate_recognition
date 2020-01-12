# Load data and set pandas options to display the full dataset if needed
import re
import pandas as pd
from Scripts import utils
from Scripts import Properties
from pymongo import MongoClient


def main():
    properties = Properties.Properties
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', -1)
    restaurant_data = pd.read_csv(properties.ORIGINAL_DATA_DIR, sep='\t')
    restaurant_data = restaurant_data.set_index(['id'], drop=False)
    restaurant_data.head()
    restaurant_data_original = restaurant_data.copy()
    # Load the gold standard duplicates to calculate metrics
    true_duplicates = pd.read_csv(properties.GOLD_STANDARD_DIR, sep='\t')
    print('Duplicates without any preprocessing')
    duplicates_bool = utils.get_duplicates_bool(restaurant_data)
    print('Metrics without any preprocessing')
    detected_duplicates = restaurant_data[duplicates_bool == True]
    utils.print_metrics(restaurant_data, detected_duplicates, true_duplicates)
    # Remove special characters from phone, address, name and city to detect duplicates
    restaurant_data = utils.remove_special_characters(restaurant_data)
    restaurant_data = utils.trim_multiple_blanks(restaurant_data)
    # Remove the direction in address and name because it's inconsistent over the dataset
    direction_regex = re.compile('(( |^)((south)|(east)|(west)|(north)|(ne)|(se)|(nw)|(sw)|s|w|e|n)( |$))')
    restaurant_data.address = restaurant_data.address.map(lambda x: direction_regex.sub(' ', x))
    restaurant_data.name = restaurant_data.name.map(lambda x: direction_regex.sub(' ', x))
    restaurant_data.city = restaurant_data.city.map(lambda x: direction_regex.sub(' ', x))
    restaurant_data = utils.trim_multiple_blanks(restaurant_data)
    print('Duplicates after removing generic clearing')
    duplicates_bool = utils.get_duplicates_bool(restaurant_data)
    print('Metrics after generic clearing')
    detected_duplicates = restaurant_data[duplicates_bool == True]
    utils.print_metrics(restaurant_data, detected_duplicates, true_duplicates)
    # Map multiple occurrences of the same city in different writing
    # It could also be a good idea to map all city parts to one city (i.e. hollywood -> los angeles)
    city_map = {'la': 'los angeles', 'new york city': 'new york'}
    restaurant_data.city = restaurant_data.city.replace(city_map)
    restaurant_data = utils.trim_multiple_blanks(restaurant_data)
    print('Duplicates after clearing city')
    duplicates_bool = utils.get_duplicates_bool(restaurant_data)
    print('Metrics after clearing city')
    detected_duplicates = restaurant_data[duplicates_bool == True]
    utils.print_metrics(restaurant_data, detected_duplicates, true_duplicates)
    print('length of unique addresses before clearing ' + str(len(restaurant_data.address.unique())))
    # Remove unnecessary explaination parts from the address string for a more accurate duplicate detection
    restaurant_data['address'] = restaurant_data['address'].str.split(r' between| off| near| at| in').str[0]
    # Remove appendixes of numbers because they are inconsistent over the dataset
    restaurant_data.address = restaurant_data.address.map(lambda x: re.sub(r"(?<=\d)(st|nd|rd|th)\b", '', x))
    # Standardize the address even more
    address_num_map = {'first': '1', 'second': '2', 'third': '3', 'fourth': '4', 'fifth': '5', 'sixth': '6',
                       'seventh': '7', 'eighth': '8', 'ninth': '9', 'tenth': '10', 'eleventh': '11', 'twelfth': '12'}
    address_name_map = {'la': 'los angeles', 'ave': 'avenue', 'rd': 'road', 'blv': 'boulevard',
                        'blvd': 'boulevard', 'st': 'street'}
    address_map = {**address_name_map, **address_num_map}
    restaurant_data.address = restaurant_data.address.map(
        lambda x: ' '.join([address_map.get(i, i) for i in x.split()]))
    restaurant_data = utils.trim_multiple_blanks(restaurant_data)
    print('Unique addresses after clearing ' + str(len(restaurant_data.address.unique())))
    print('Duplicates after clearing the address')
    duplicates_bool = utils.get_duplicates_bool(restaurant_data)
    print('Metrics after clearing the address')
    detected_duplicates = restaurant_data[duplicates_bool == True]
    utils.print_metrics(restaurant_data, detected_duplicates, true_duplicates)
    print('Unique names before clearing name: ' + str(len(restaurant_data.name.unique())))
    unique_city_list = restaurant_data.city.unique()
    restaurant_data.name = restaurant_data.name.str.split(r' between| off| near| at| in| of').str[0]
    city_regex = re.compile('the|restaurant|and|new york city|' + '|'.join(map(re.escape, unique_city_list)))
    restaurant_data.name = [city_regex.sub('', name) for name in restaurant_data.name]
    restaurant_data.name = restaurant_data.name.apply(lambda x: ' '.join(sorted(x.split(' '))))
    restaurant_data = utils.trim_multiple_blanks(restaurant_data)
    print('Unique names after clearing name: ' + str(len(restaurant_data.name.unique())))
    print('Duplicates after clearing name')
    duplicates_bool = utils.get_duplicates_bool(restaurant_data)
    print('Metrics after clearing')
    detected_duplicates = restaurant_data[duplicates_bool == True]
    detected_non_duplicates = restaurant_data[duplicates_bool == False]
    utils.print_metrics(restaurant_data, detected_duplicates, true_duplicates)
    # Check the dataset without duplicates
    restaurant_data[restaurant_data['id'].isin(detected_duplicates['id']) == False].head()
    final_data = utils.get_final_dataset(restaurant_data_original, restaurant_data)
    final_data.head()
    client = MongoClient(properties.MONGODB_CONNECTION_STRING, serverSelectionTimeoutMS=60)
    db = client[properties.MONGODB_DB_NAME]
    collection = db[properties.MONGODB_COLLECTION_NAME]
    data = final_data.to_dict(orient='records')
    collection.insert_many(data)
    print('Successfully stored the data into mongodb')
    client.close()


if __name__ == '__main__':
    main()
