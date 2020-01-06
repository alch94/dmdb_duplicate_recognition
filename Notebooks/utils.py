import re


def print_metrics(restaurant_data, detected_duplicates, true_duplicates):

    # Check the quality of the duplicate detection
    restaurant_data_count = len(restaurant_data)
    my_duplicate_ids = detected_duplicates['id']
    my_duplicate_count = len(my_duplicate_ids)
    real_duplicates_count = len(true_duplicates)
    true_positives_count = len(my_duplicate_ids[my_duplicate_ids.isin(true_duplicates.id2)])
    false_positives_count = len(my_duplicate_ids[my_duplicate_ids.isin(true_duplicates.id2) == False])
    false_negatives = real_duplicates_count - true_positives_count
    true_negatives = restaurant_data_count - real_duplicates_count - false_positives_count
    accuracy = (true_positives_count + true_negatives) / (true_positives_count + true_negatives + false_positives_count + false_negatives)
    precision = true_positives_count / my_duplicate_count
    recall = true_positives_count / (true_positives_count + false_negatives)


    print('All entries in original dataset: ' + str(restaurant_data_count))
    print('Detected duplicates (all): ' + str(my_duplicate_count))
    print('Real duplicates (from gold standard): ' + str(real_duplicates_count))
    print('True positives: ' + str(true_positives_count))
    print('True negatives: ' + str(true_negatives))
    print('False positives: ' + str(false_positives_count))
    print('False negatives: ' + str(false_negatives))
    print('Accuracy ' + str(accuracy))
    print('Precision: ' + str(precision))
    print('Recall: ' + str(recall))


def remove_special_characters(restaurant_data):
    restaurant_data.phone = restaurant_data.phone.map(lambda x: re.sub(r'\W+', '', x))
    restaurant_data.address = restaurant_data.address.map(lambda x: re.sub(r'[^a-zA-Z0-9 ]+', '', x))
    restaurant_data.name = restaurant_data.name.map(lambda x: re.sub(r'[^a-zA-Z0-9 ]+', '', x))
    restaurant_data.city = restaurant_data.city.map(lambda x: re.sub(r'[^a-zA-Z0-9 ]+', '', x))
    return restaurant_data


def get_duplicates_bool(restaurant_data):
    # Get a Series of all duplicate entries
    address_city_phone =['id']# ['address', 'city', 'phone']
    address_name_phone = ['address', 'name', 'phone']
    address_city_name = ['address', 'city', 'name']
    name_city_phone = ['name', 'city', 'phone']
    address_city_name_phone = ['address', 'city', 'name', 'phone']
    duplicates_address_city_phone = restaurant_data.duplicated(subset=address_city_phone)
    duplicates_address_name_phone = restaurant_data.duplicated(subset=address_name_phone)
    duplicates_address_city_name = restaurant_data.duplicated(subset=address_city_name)
    duplicates_name_city_phone = restaurant_data.duplicated(subset=name_city_phone)
    duplicates_bool = duplicates_address_city_phone | duplicates_address_name_phone | duplicates_address_city_name | duplicates_name_city_phone
    # Check for the duplicates in the four important columns in our dataset
    print('Duplicates in address, city and phone' + str(
        duplicates_address_city_phone.sum()))
    print('Duplicates in address name and phone: ' + str(
        duplicates_address_name_phone.sum()))
    print('Duplicates in address city and name: ' + str(
        duplicates_address_city_name.sum()))
    print('Duplicates in name city and phone' + str(duplicates_name_city_phone.sum()))
    print('Duplicates in address, city, name and phone: ' + str(
        restaurant_data.duplicated(subset=address_city_name_phone).sum()))
    print('duplicates in 3 columns of address, city, name and phone' + str(duplicates_bool.sum()))
    return duplicates_bool
