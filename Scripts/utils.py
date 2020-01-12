import re

from more_itertools.more import only


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
    accuracy = (true_positives_count + true_negatives) / (
                true_positives_count + true_negatives + false_positives_count + false_negatives)
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
    restaurant_data.address = restaurant_data.address.map(lambda x: re.sub(r"[^a-zA-Z0-9 ]+", '', x))
    restaurant_data.name = restaurant_data.name.map(lambda x: re.sub(r"('s)|[^a-zA-Z0-9 ]+", '', x))
    restaurant_data.city = restaurant_data.city.map(lambda x: re.sub(r'[^a-zA-Z0-9 ]+', '', x))
    return restaurant_data


def get_duplicates_bool(restaurant_data):
    # Get a Series of all duplicate entries
    address_name_phone = ['address', 'name', 'phone']
    address_city_name = ['address', 'city', 'name']
    name_city_phone = ['name', 'city', 'phone']
    address_city_name_phone = ['address', 'city', 'name', 'phone']
    duplicates_city = restaurant_data.duplicated(subset=['city'])
    duplicates_name = restaurant_data.duplicated(subset=['name'])
    duplicates_address = restaurant_data.duplicated(subset=['address'])
    duplicates_phone = restaurant_data.duplicated(subset=['phone'])
    duplicates_address_name_phone = restaurant_data.duplicated(subset=address_name_phone)
    duplicates_address_city_name = restaurant_data.duplicated(subset=address_city_name)
    duplicates_name_city_phone = restaurant_data.duplicated(subset=name_city_phone)
    duplicates_bool = duplicates_address_name_phone | duplicates_address_city_name | duplicates_name_city_phone
    # Check for the duplicates in the four important columns in our dataset
    print('Duplicates in address: ' + str(
        duplicates_address.sum()))
    print('Duplicates in name: ' + str(
        duplicates_name.sum()))
    print('Duplicates in phone: ' + str(
        duplicates_phone.sum()))
    print('Duplicates in city: ' + str(
        duplicates_city.sum()))
    print('Duplicates in address name and phone: ' + str(
        duplicates_address_name_phone.sum()))
    print('Duplicates in address city and name: ' + str(
        duplicates_address_city_name.sum()))
    print('Duplicates in name city and phone' + str(duplicates_name_city_phone.sum()))
    print('Duplicates in address, city, name and phone: ' + str(
        restaurant_data.duplicated(subset=address_city_name_phone).sum()))
    print('duplicates in 3 columns of address, city, name and phone' + str(duplicates_bool.sum()))
    return duplicates_bool


def trim_multiple_blanks(restaurant_data):
    restaurant_data.name = restaurant_data.name.replace('\s+', ' ', regex=True)
    restaurant_data.address = restaurant_data.address.replace('\s+', ' ', regex=True)
    restaurant_data.city = restaurant_data.city.replace('\s+', ' ', regex=True)
    restaurant_data.phone = restaurant_data.phone.replace('\s+', ' ', regex=True)
    restaurant_data.name = restaurant_data.name.str.strip()
    restaurant_data.address = restaurant_data.address.str.strip()
    restaurant_data.phone = restaurant_data.phone.str.strip()
    restaurant_data.city = restaurant_data.city.str.strip()
    return restaurant_data


def get_final_dataset(restaurant_data_original, restaurant_data_cleared):
    address_name_phone = ['address', 'name', 'phone']
    address_city_name = ['address', 'city', 'name']
    name_city_phone = ['name', 'city', 'phone']
    duplicates_address_name_phone = restaurant_data_cleared.duplicated(subset=address_name_phone, keep=False)
    duplicates_address_city_name = restaurant_data_cleared.duplicated(subset=address_city_name, keep=False)
    duplicates_name_city_phone = restaurant_data_cleared.duplicated(subset=name_city_phone, keep=False)
    all_duplicates_bool = duplicates_address_name_phone | duplicates_address_city_name | duplicates_name_city_phone
    only_duplicates = restaurant_data_cleared[all_duplicates_bool]
    duplicate_indices = {}
    for row1_idx, row1 in only_duplicates.iterrows():
        cur_index = row1_idx
        row_1_imp_cols_1 = row1[address_name_phone]
        row_1_imp_cols_2 = row1[address_city_name]
        row_1_imp_cols_3 = row1[name_city_phone]
        for row2_idx, row2 in only_duplicates[only_duplicates.id > row1_idx].iterrows():
            row_2_imp_cols_1 = row2[address_name_phone]
            row_2_imp_cols_2 = row2[address_city_name]
            row_2_imp_cols_3 = row2[name_city_phone]
            if (row_1_imp_cols_1.equals(row_2_imp_cols_1) or
                    row_1_imp_cols_2.equals(row_2_imp_cols_2) or
                    row_1_imp_cols_3.equals(row_2_imp_cols_3)):
                if duplicate_indices.get(cur_index) is None:
                    duplicate_indices[cur_index] = []
                duplicate_indices[cur_index].append(row2_idx)

    for original_index in duplicate_indices:
        original_cleared_entry = restaurant_data_cleared.loc[original_index]
        original_entry = restaurant_data_original.loc[original_index]
        for duplicate_index in duplicate_indices.get(original_index):
            duplicate_cleared_entry = restaurant_data_cleared.loc[duplicate_index]
            duplicate_entry = restaurant_data_original.loc[duplicate_index]
            if original_cleared_entry.phone != duplicate_cleared_entry.phone:
                restaurant_data_original.loc[original_index, 'phone'] = original_entry.phone + ', \n ' + duplicate_entry.phone
                print(restaurant_data_original.loc[original_index].phone)
            if original_cleared_entry.city != duplicate_cleared_entry.city:
                restaurant_data_original.loc[original_index, 'city'] = [original_entry.city + ', \n ' + duplicate_entry.city]
                if original_cleared_entry.address != duplicate_cleared_entry.address:
                    restaurant_data_original.loc[original_index, 'address'] = [
                        original_entry.address + ', \n ' + duplicate_entry.address]
            restaurant_data_original = restaurant_data_original.drop([duplicate_index])
    return restaurant_data_original
