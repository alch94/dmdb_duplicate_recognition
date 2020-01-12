class Properties:
    # Location of the original dataset
    ORIGINAL_DATA_DIR = '../Data/restaurants.tsv'
    # Location of the gold standard dataset
    GOLD_STANDARD_DIR = '../Data/restaurants_DPL.tsv'
    # Mongodb connection string
    #TODO: Don't forget to enter username and password
    MONGODB_CONNECTION_STRING = 'mongodb+srv://<User>:<Password>@cluster0-uqgxm.mongodb.net/test?retryWrites=true&w=majority'
    # Database name in which you want to write the cleared. This database needs to be created before running the script
    MONGODB_DB_NAME = 'dmdb_db'
    # Mongodb Collection name in which you want to write the data. This collection is generated automatically if it does not exist
    MONGODB_COLLECTION_NAME = 'restaurants_no_dupls'
